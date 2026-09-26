from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from .models import Medication, StockBatch, StockMovement, Prescription


@transaction.atomic
def add_stock(
    *,
    medication,
    stock_batch,
    quantity,
    performed_by,
    reference="",
    notes="",
):
    """
    Add stock to a batch and create an audit movement.
    """

    if quantity <= 0:
        raise ValidationError("Quantity must be greater than zero.")

    if stock_batch.medication_id != medication.id:
        raise ValidationError(
            "The selected stock batch does not belong to this medication."
        )

    batch = (
        StockBatch.objects
        .select_for_update()
        .get(pk=stock_batch.pk)
    )

    batch.quantity += quantity
    batch.save(update_fields=["quantity", "updated_at"])

    movement = StockMovement.objects.create(
        medication=medication,
        stock_batch=batch,
        movement_type=StockMovement.MovementType.PURCHASE,
        quantity=quantity,
        reference=reference,
        notes=notes,
        performed_by=performed_by,
    )

    return movement


@transaction.atomic
def remove_stock(
    *,
    medication,
    stock_batch,
    quantity,
    performed_by,
    movement_type,
    reference="",
    notes="",
):
    """
    Remove stock from a batch and create an audit movement.
    """

    if quantity <= 0:
        raise ValidationError("Quantity must be greater than zero.")

    if movement_type not in {
        StockMovement.MovementType.DISPENSE,
        StockMovement.MovementType.RETURN,
        StockMovement.MovementType.ADJUSTMENT,
        StockMovement.MovementType.EXPIRED,
        StockMovement.MovementType.DAMAGED,
    }:
        raise ValidationError(
            "Invalid stock removal movement type."
        )

    if stock_batch.medication_id != medication.id:
        raise ValidationError(
            "The selected stock batch does not belong to this medication."
        )

    batch = (
        StockBatch.objects
        .select_for_update()
        .get(pk=stock_batch.pk)
    )

    if batch.quantity < quantity:
        raise ValidationError(
            f"Insufficient stock. "
            f"Available: {batch.quantity}, requested: {quantity}."
        )

    batch.quantity -= quantity
    batch.save(update_fields=["quantity", "updated_at"])

    movement = StockMovement.objects.create(
        medication=medication,
        stock_batch=batch,
        movement_type=movement_type,
        quantity=-quantity,
        reference=reference,
        notes=notes,
        performed_by=performed_by,
    )

    return movement


@transaction.atomic
def dispense_prescription(
    *,
    prescription,
    performed_by,
):
    """
    Dispense an entire prescription using FEFO.

    FEFO = First Expiry, First Out.

    The entire prescription is processed atomically:
    if any medication cannot be fully supplied,
    no stock is changed.
    """

    # Lock the prescription itself.
    prescription = (
        Prescription.objects
        .select_for_update()
        .select_related("patient")
        .get(pk=prescription.pk)
    )

    # The prescription must be ready for pharmacy.
    if prescription.status != Prescription.Status.COMPLETED:
        raise ValidationError(
            "Only finalized prescriptions can be dispensed."
        )

    items = list(
        prescription.items
        .select_related("medication")
        .order_by("id")
    )

    if not items:
        raise ValidationError(
            "This prescription contains no medications."
        )

    today = timezone.localdate()

    # ---------------------------------------------------------
    # STEP 1: Lock all potentially usable stock batches
    # ---------------------------------------------------------

    medication_ids = {
        item.medication_id
        for item in items
    }

    batches = list(
        StockBatch.objects
        .select_for_update()
        .filter(
            medication_id__in=medication_ids,
            is_active=True,
            quantity__gt=0,
            expiry_date__gte=today,
        )
        .order_by(
            "medication_id",
            "expiry_date",
            "id",
        )
    )

    batches_by_medication = {}

    for batch in batches:
        batches_by_medication.setdefault(
            batch.medication_id,
            []
        ).append(batch)

    # ---------------------------------------------------------
    # STEP 2: Calculate the FEFO allocation for EVERYTHING
    # before changing any stock.
    # ---------------------------------------------------------

    allocations = []

    for item in items:

        remaining = item.quantity

        medication_batches = batches_by_medication.get(
            item.medication_id,
            [],
        )

        for batch in medication_batches:

            if remaining <= 0:
                break

            quantity_from_batch = min(
                remaining,
                batch.quantity,
            )

            if quantity_from_batch <= 0:
                continue

            allocations.append(
                {
                    "item": item,
                    "batch": batch,
                    "quantity": quantity_from_batch,
                }
            )

            remaining -= quantity_from_batch

        # Not enough stock for this medication.
        if remaining > 0:
            available = sum(
                batch.quantity
                for batch in medication_batches
            )

            raise ValidationError(
                f"Insufficient stock for "
                f"{item.medication}. "
                f"Required: {item.quantity}. "
                f"Available: {available}."
            )

    # ---------------------------------------------------------
    # STEP 3: Apply all allocations
    # ---------------------------------------------------------

    movements = []

    for allocation in allocations:

        batch = allocation["batch"]
        quantity = allocation["quantity"]

        batch.quantity -= quantity

        batch.save(
            update_fields=[
                "quantity",
                "updated_at",
            ]
        )

        movement = StockMovement.objects.create(
            medication=batch.medication,
            stock_batch=batch,
            movement_type=StockMovement.MovementType.DISPENSE,
            quantity=-quantity,
            reference=prescription.prescription_id,
            notes=(
                f"Dispensed for prescription "
                f"{prescription.prescription_id}."
            ),
            performed_by=performed_by,
        )

        movements.append(movement)

    # ---------------------------------------------------------
    # STEP 4: Mark prescription as dispensed
    # ---------------------------------------------------------

    prescription.status = Prescription.Status.DISPENSED

    prescription.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    return movements