from django.conf import settings
from django.db import models

from clinic.encounters.models import Encounter


class Consultation(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        COMPLETED = "COMPLETED", "Completed"

    consultation_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
    )

    encounter = models.OneToOneField(
        Encounter,
        on_delete=models.PROTECT,
        related_name="consultation",
    )

    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="consultations",
    )

    chief_complaint = models.TextField(
        blank=True,
        help_text="Main reason the patient came to the clinic",
    )

    history_of_present_illness = models.TextField(
        blank=True,
    )

    medical_history = models.TextField(
        blank=True,
    )

    physical_examination = models.TextField(
        blank=True,
    )

    assessment = models.TextField(
        blank=True,
        help_text="Doctor's clinical assessment",
    )

    diagnosis = models.TextField(
        blank=True,
    )

    treatment_plan = models.TextField(
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.consultation_id:
            last_consultation = Consultation.objects.order_by("-id").first()

            if last_consultation:
                next_number = last_consultation.id + 1
            else:
                next_number = 1

            self.consultation_id = f"CON-{next_number:06d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.consultation_id} - {self.encounter.patient.full_name}"