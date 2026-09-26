from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from core.department_access import department_required
from .models import Invoice
from .services import record_payment


@department_required("BILLING")
def invoice_queue(request):
    invoices = (
        Invoice.objects
        .select_related("encounter", "encounter__patient", "created_by")
        .prefetch_related("items", "payments")
        .filter(
            status__in=[
                Invoice.Status.UNPAID,
                Invoice.Status.PARTIALLY_PAID,
            ]
        )
        .order_by("-created_at")
    )

    return render(
        request,
        "billing/invoice_queue.html",
        {
            "invoices": invoices,
        },
    )


@department_required("BILLING")
def receive_payment(request, invoice_id):
    invoice = get_object_or_404(
        Invoice.objects
        .select_related(
            "encounter",
            "encounter__patient",
        )
        .prefetch_related(
            "items",
            "payments",
        ),
        id=invoice_id,
    )

    total = invoice.total_amount
    paid = sum(payment.amount for payment in invoice.payments.all())
    balance = total - paid

    if request.method == "POST":

        amount = request.POST.get("amount", "").strip()
        method = request.POST.get("method", "").strip()
        reference = request.POST.get("reference", "").strip()
        notes = request.POST.get("notes", "").strip()

        try:
            amount = Decimal(amount)

            payment, updated_invoice = record_payment(
                invoice_id=invoice.id,
                amount=amount,
                method=method,
                received_by=request.user,
                reference=reference,
                notes=notes,
            )

            messages.success(
                request,
                f"Payment {payment.payment_id} received successfully. "
                f"Invoice {updated_invoice.invoice_id} is now {updated_invoice.get_status_display().lower()}.",
            )

            return redirect("billing:invoice_queue")

        except (ValidationError, ValueError, TypeError) as exc:

            if hasattr(exc, "messages"):
                error_message = " ".join(exc.messages)
            else:
                error_message = str(exc)

            messages.error(request, error_message)

    return render(
        request,
        "billing/receive_payment.html",
        {
            "invoice": invoice,
            "total": total,
            "paid": paid,
            "balance": balance,
        },
    )