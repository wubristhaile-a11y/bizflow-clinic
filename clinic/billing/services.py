from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Invoice, Payment


@transaction.atomic
def update_invoice_status(invoice_id):
    invoice = (
        Invoice.objects
        .select_for_update()
        .get(pk=invoice_id)
    )

    total = invoice.total_amount

    paid = sum(
        payment.amount
        for payment in invoice.payments.all()
    )

    if paid >= total and total > Decimal("0.00"):
        invoice.status = Invoice.Status.PAID

        for item in invoice.items.select_related("clinical_order"):
            order = item.clinical_order

            if order.status == order.Status.AWAITING_PAYMENT:
                order.status = order.Status.PAID
                order.save(
                    update_fields=["status", "updated_at"]
                )

    elif paid > Decimal("0.00"):
        invoice.status = Invoice.Status.PARTIALLY_PAID

    else:
        invoice.status = Invoice.Status.UNPAID

    invoice.save(
        update_fields=["status", "updated_at"]
    )

    return invoice


@transaction.atomic
def record_payment(
    invoice_id,
    amount,
    method,
    received_by,
    reference="",
    notes="",
):
    invoice = (
        Invoice.objects
        .select_for_update()
        .get(pk=invoice_id)
    )

    # ---------------------------------------------------------
    # Basic payment validation
    # ---------------------------------------------------------

    amount = Decimal(amount)

    if amount <= Decimal("0.00"):
        raise ValidationError(
            "Payment amount must be greater than zero."
        )

    if invoice.status == Invoice.Status.CANCELLED:
        raise ValidationError(
            "Cannot make a payment against a cancelled invoice."
        )

    # ---------------------------------------------------------
    # Calculate current balance
    # ---------------------------------------------------------

    total = invoice.total_amount

    paid = sum(
        payment.amount
        for payment in invoice.payments.all()
    )

    balance = total - paid

    # ---------------------------------------------------------
    # Prevent overpayment
    # ---------------------------------------------------------

    if balance <= Decimal("0.00"):
        raise ValidationError(
            "This invoice has already been fully paid."
        )

    if amount > balance:
        raise ValidationError(
            f"Payment exceeds the remaining balance "
            f"of {balance:.2f} ETB."
        )

    # ---------------------------------------------------------
    # Create payment
    # ---------------------------------------------------------

    payment = Payment.objects.create(
        invoice=invoice,
        amount=amount,
        method=method,
        received_by=received_by,
        reference=reference,
        notes=notes,
    )

    # ---------------------------------------------------------
    # Update invoice and clinical order status
    # ---------------------------------------------------------

    invoice = update_invoice_status(invoice.id)

    return payment, invoice