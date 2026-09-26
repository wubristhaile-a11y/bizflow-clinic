from django.conf import settings
from django.db import models

from clinic.encounters.models import Encounter
from clinic.orders.models import ClinicalOrder


class Invoice(models.Model):
    class Status(models.TextChoices):
        UNPAID = "UNPAID", "Unpaid"
        PARTIALLY_PAID = "PARTIALLY_PAID", "Partially Paid"
        PAID = "PAID", "Paid"
        CANCELLED = "CANCELLED", "Cancelled"

    invoice_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
    )

    encounter = models.ForeignKey(
        Encounter,
        on_delete=models.PROTECT,
        related_name="invoices",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UNPAID,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_invoices",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.invoice_id:
            last_invoice = Invoice.objects.order_by("-id").first()

            if last_invoice:
                next_number = last_invoice.id + 1
            else:
                next_number = 1

            self.invoice_id = f"INV-{next_number:06d}"

        super().save(*args, **kwargs)

    @property
    def total_amount(self):
        return sum(
            item.amount
            for item in self.items.all()
        )

    def __str__(self):
        return f"{self.invoice_id} - {self.encounter.patient.full_name}"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="items",
    )

    clinical_order = models.OneToOneField(
        ClinicalOrder,
        on_delete=models.PROTECT,
        related_name="invoice_item",
    )

    description = models.CharField(
        max_length=200,
    )

    quantity = models.PositiveIntegerField(
        default=1,
    )

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.amount = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description} - {self.amount} ETB"

class Payment(models.Model):
    class Method(models.TextChoices):
        CASH = "CASH", "Cash"
        BANK_TRANSFER = "BANK_TRANSFER", "Bank Transfer"
        CARD = "CARD", "Card"
        MOBILE_MONEY = "MOBILE_MONEY", "Mobile Money"
        OTHER = "OTHER", "Other"

    payment_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
    )

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.PROTECT,
        related_name="payments",
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    method = models.CharField(
        max_length=30,
        choices=Method.choices,
        default=Method.CASH,
    )

    reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="Transaction or receipt reference, if applicable",
    )

    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="received_payments",
    )

    notes = models.TextField(
        blank=True,
    )

    paid_at = models.DateTimeField(
        auto_now_add=True,
    )

    def save(self, *args, **kwargs):
        if not self.payment_id:
            last_payment = Payment.objects.order_by("-id").first()

            if last_payment:
                next_number = last_payment.id + 1
            else:
                next_number = 1

            self.payment_id = f"PAY-{next_number:06d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.payment_id} - {self.amount} ETB"