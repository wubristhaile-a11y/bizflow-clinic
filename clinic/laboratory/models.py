from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from clinic.orders.models import ClinicalOrder


class LabResult(models.Model):

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        COMPLETED = "COMPLETED", "Completed"
        REVIEWED = "REVIEWED", "Reviewed"

    result_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
    )

    clinical_order = models.OneToOneField(
        ClinicalOrder,
        on_delete=models.PROTECT,
        related_name="lab_result",
    )

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="lab_results_performed",
    )

    result = models.TextField()

    notes = models.TextField(
        blank=True,
        help_text="Additional laboratory notes or comments.",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    performed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def clean(self):
        if self.clinical_order.service.department.code != "LAB":
            raise ValidationError(
                "This clinical order does not belong to the Laboratory department."
            )

        if self.clinical_order.status not in [
            ClinicalOrder.Status.PAID,
            ClinicalOrder.Status.IN_PROGRESS,
            ClinicalOrder.Status.COMPLETED,
            ClinicalOrder.Status.RESULT_AVAILABLE,
            ClinicalOrder.Status.DOCTOR_REVIEWED,
        ]:
            raise ValidationError(
                "Laboratory work cannot be performed before the order is paid."
            )

    def save(self, *args, **kwargs):
        if not self.result_id:
            last_result = LabResult.objects.order_by("-id").first()

            next_number = (
                last_result.id + 1
                if last_result
                else 1
            )

            self.result_id = f"LAB-{next_number:06d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.result_id