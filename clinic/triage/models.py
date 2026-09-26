from django.conf import settings
from django.db import models

from clinic.encounters.models import Encounter


class TriageRecord(models.Model):
    encounter = models.OneToOneField(
        Encounter,
        on_delete=models.PROTECT,
        related_name="triage",
    )

    systolic_bp = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Systolic blood pressure in mmHg",
    )

    diastolic_bp = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Diastolic blood pressure in mmHg",
    )

    temperature = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Temperature in °C",
    )

    pulse = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Pulse rate in beats per minute",
    )

    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weight in kilograms",
    )

    blood_sugar = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Blood sugar in mg/dL",
    )

    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="triage_records",
    )

    recorded_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    notes = models.TextField(
        blank=True,
    )

    def __str__(self):
        return f"Triage - {self.encounter.encounter_id}"