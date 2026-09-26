from django.db import models
from django.conf import settings
from django.db import models

from clinic.consultations.models import Consultation
from clinic.patients.models import Patient

class Medication(models.Model):

    class DosageForm(models.TextChoices):
        TABLET = "TABLET", "Tablet"
        CAPSULE = "CAPSULE", "Capsule"
        SYRUP = "SYRUP", "Syrup"
        SUSPENSION = "SUSPENSION", "Suspension"
        INJECTION = "INJECTION", "Injection"
        CREAM = "CREAM", "Cream"
        OINTMENT = "OINTMENT", "Ointment"
        DROPS = "DROPS", "Drops"
        INHALER = "INHALER", "Inhaler"
        SUPPOSITORY = "SUPPOSITORY", "Suppository"
        OTHER = "OTHER", "Other"

    name = models.CharField(
        max_length=200,
        help_text="Commercial or displayed medication name",
    )

    generic_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Generic/active ingredient name",
    )

    strength = models.CharField(
        max_length=100,
        blank=True,
        help_text="Example: 500 mg or 250 mg/5 mL",
    )

    dosage_form = models.CharField(
        max_length=20,
        choices=DosageForm.choices,
        default=DosageForm.TABLET,
    )

    unit = models.CharField(
        max_length=50,
        default="unit",
        help_text="Example: tablet, capsule, bottle, tube",
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        parts = [self.name]

        if self.strength:
            parts.append(self.strength)

        parts.append(self.get_dosage_form_display())

        return " — ".join(parts)




class Prescription(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        COMPLETED = "COMPLETED", "Completed"
        DISPENSED = "DISPENSED", "Dispensed"
        CANCELLED = "CANCELLED", "Cancelled"

    prescription_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
    )

    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.PROTECT,
        related_name="prescriptions",
    )

    patient = models.ForeignKey(
        Patient,
        on_delete=models.PROTECT,
        related_name="prescriptions",
    )

    prescribed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="prescriptions",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.prescription_id:
            last_prescription = Prescription.objects.order_by("-id").first()
            next_number = last_prescription.id + 1 if last_prescription else 1
            self.prescription_id = f"PRX-{next_number:06d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.prescription_id} - {self.patient.full_name}"


class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name="items",
    )

    medication = models.ForeignKey(
        Medication,
        on_delete=models.PROTECT,
        related_name="prescription_items",
    )

    dose = models.CharField(
        max_length=100,
        help_text="Example: 1 tablet",
    )

    frequency = models.CharField(
        max_length=100,
        help_text="Example: 3 times daily",
    )

    duration = models.CharField(
        max_length=100,
        help_text="Example: 7 days",
    )

    quantity = models.PositiveIntegerField(
        help_text="Total quantity to dispense",
    )

    instructions = models.TextField(
        blank=True,
        help_text="Example: Take after meals",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.medication} - {self.prescription.prescription_id}"

class StockBatch(models.Model):
    medication = models.ForeignKey(
        Medication,
        on_delete=models.PROTECT,
        related_name="stock_batches",
    )

    batch_number = models.CharField(
        max_length=100,
        help_text="Manufacturer or supplier batch number",
    )

    expiry_date = models.DateField()

    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Purchase price per unit",
    )

    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Selling price per unit",
    )

    quantity = models.PositiveIntegerField(
        default=0,
        help_text="Current available quantity",
    )

    received_at = models.DateTimeField(
        auto_now_add=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return (
            f"{self.medication} - "
            f"Batch {self.batch_number} - "
            f"{self.quantity} available"
        )

class StockMovement(models.Model):
    class MovementType(models.TextChoices):
        PURCHASE = "PURCHASE", "Purchase"
        DISPENSE = "DISPENSE", "Dispense"
        RETURN = "RETURN", "Return"
        ADJUSTMENT = "ADJUSTMENT", "Adjustment"
        EXPIRED = "EXPIRED", "Expired"
        DAMAGED = "DAMAGED", "Damaged"

    medication = models.ForeignKey(
        Medication,
        on_delete=models.PROTECT,
        related_name="stock_movements",
    )

    stock_batch = models.ForeignKey(
        StockBatch,
        on_delete=models.PROTECT,
        related_name="movements",
    )

    movement_type = models.CharField(
        max_length=20,
        choices=MovementType.choices,
    )

    quantity = models.IntegerField(
        help_text="Positive for stock added, negative for stock removed",
    )

    reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="Related document, prescription, invoice, adjustment number, etc.",
    )

    notes = models.TextField(
        blank=True,
    )

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="stock_movements",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return (
            f"{self.medication} - "
            f"{self.get_movement_type_display()} - "
            f"{self.quantity}"
        )