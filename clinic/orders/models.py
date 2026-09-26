from django.conf import settings
from django.db import models

from clinic.encounters.models import Encounter
from clinic.services.models import Service
from clinic.consultations.models import Consultation


class ClinicalOrder(models.Model):

    class Status(models.TextChoices):
        ORDERED = "ORDERED", "Ordered"
        AWAITING_PAYMENT = "AWAITING_PAYMENT", "Awaiting Payment"
        PAID = "PAID", "Paid"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        RESULT_AVAILABLE = "RESULT_AVAILABLE", "Result Available"
        DOCTOR_REVIEWED = "DOCTOR_REVIEWED", "Doctor Reviewed"
        CANCELLED = "CANCELLED", "Cancelled"

    order_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
    )

    encounter = models.ForeignKey(
        Encounter,
        on_delete=models.PROTECT,
        related_name="clinical_orders",
    )

    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.PROTECT,
        related_name="clinical_orders",
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name="clinical_orders",
    )

    ordered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="clinical_orders",
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.ORDERED,
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price captured at the time of ordering, in ETB",
    )

    clinical_notes = models.TextField(
        blank=True,
        help_text="Instructions or notes from the ordering doctor",
    )

    ordered_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def save(self, *args, **kwargs):
        if not self.order_id:
            last_order = ClinicalOrder.objects.order_by("-id").first()

            if last_order:
                next_number = last_order.id + 1
            else:
                next_number = 1

            self.order_id = f"ORD-{next_number:06d}"

        if not self.price:
            self.price = self.service.price

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.order_id} - "
            f"{self.encounter.patient.full_name} - "
            f"{self.service.name}"
        )