from django.conf import settings
from django.db import models

from clinic.patients.models import Patient


class Encounter(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    encounter_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
    )

    patient = models.ForeignKey(
        Patient,
        on_delete=models.PROTECT,
        related_name="encounters",
    )

    attended_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="attended_encounters",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )

    visit_reason = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def save(self, *args, **kwargs):
        if not self.encounter_id:
            last_encounter = Encounter.objects.order_by("-id").first()

            if last_encounter:
                next_number = last_encounter.id + 1
            else:
                next_number = 1

            self.encounter_id = f"ENC-{next_number:06d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.encounter_id} - {self.patient.full_name}"