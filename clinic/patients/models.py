from django.db import models


class Patient(models.Model):
    class Sex(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"
        OTHER = "O", "Other"

    patient_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
    )

    full_name = models.CharField(max_length=200)

    age = models.PositiveIntegerField()

    sex = models.CharField(
        max_length=1,
        choices=Sex.choices,
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
    )

    address = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.patient_id:
            last_patient = Patient.objects.order_by("-id").first()

            if last_patient:
                next_number = last_patient.id + 1
            else:
                next_number = 1

            self.patient_id = f"BF-{next_number:06d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient_id} - {self.full_name}"