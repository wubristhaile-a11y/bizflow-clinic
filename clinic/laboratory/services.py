from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from clinic.orders.models import ClinicalOrder
from .models import LabResult


@transaction.atomic
def start_lab_order(order_id):
    """
    Move a paid laboratory order into the laboratory work queue
    and automatically create its LabResult record.
    """

    order = (
        ClinicalOrder.objects
        .select_for_update()
        .select_related("service__department")
        .get(pk=order_id)
    )

    if order.service.department.code != "LAB":
        raise ValidationError(
            "This order does not belong to the Laboratory department."
        )

    if order.status != ClinicalOrder.Status.PAID:
        raise ValidationError(
            "Only paid laboratory orders can be started."
        )

    # Create the laboratory result record automatically.
    lab_result, created = LabResult.objects.get_or_create(
        clinical_order=order,
        defaults={
            "performed_by": order.ordered_by,
            "result": "",
            "status": LabResult.Status.DRAFT,
        },
    )

    # Move the order into the laboratory work queue.
    order.status = ClinicalOrder.Status.IN_PROGRESS
    order.save(update_fields=["status", "updated_at"])

    return order, lab_result

@transaction.atomic
def complete_lab_result(
    order_id,
    performed_by,
    result,
    notes="",
):
    """
    Complete the draft laboratory result for an in-progress order
    and release it to the ordering doctor.
    """

    order = (
        ClinicalOrder.objects
        .select_for_update()
        .select_related(
            "service__department",
            "encounter__patient",
        )
        .get(pk=order_id)
    )

    if order.service.department.code != "LAB":
        raise ValidationError(
            "This order does not belong to the Laboratory department."
        )

    if order.status != ClinicalOrder.Status.IN_PROGRESS:
        raise ValidationError(
            "Only laboratory orders currently in progress "
            "can be completed."
        )

    if not result or not result.strip():
        raise ValidationError(
            "Laboratory result cannot be empty."
        )

    lab_result = (
        LabResult.objects
        .select_for_update()
        .get(clinical_order=order)
    )

    if lab_result.status != LabResult.Status.DRAFT:
        raise ValidationError(
            "This laboratory result has already been completed."
        )

    lab_result.performed_by = performed_by
    lab_result.result = result.strip()
    lab_result.notes = notes.strip()
    lab_result.status = LabResult.Status.COMPLETED
    lab_result.performed_at = timezone.now()

    lab_result.save()

    order.status = ClinicalOrder.Status.RESULT_AVAILABLE

    order.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    return lab_result, order


@transaction.atomic
def review_lab_result(order_id, reviewed_by):
    """
    Mark a laboratory result as reviewed by the
    doctor who ordered the clinical investigation.
    """

    order = (
        ClinicalOrder.objects
        .select_for_update()
        .select_related("consultation", "ordered_by")
        .get(pk=order_id)
    )

    if order.status != ClinicalOrder.Status.RESULT_AVAILABLE:
        raise ValidationError(
            "Only results that are available can be reviewed."
        )

    if order.ordered_by_id != reviewed_by.id:
        raise ValidationError(
            "Only the doctor who ordered this investigation "
            "can review the result."
        )

    lab_result = (
        LabResult.objects
        .select_for_update()
        .get(clinical_order=order)
    )

    lab_result.status = LabResult.Status.REVIEWED
    lab_result.save(
        update_fields=["status", "updated_at"]
    )

    order.status = ClinicalOrder.Status.DOCTOR_REVIEWED
    order.save(
        update_fields=["status", "updated_at"]
    )

    return lab_result, order