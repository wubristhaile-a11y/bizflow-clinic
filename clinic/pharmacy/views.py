from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import ValidationError
from clinic.consultations.models import Consultation
from .services import dispense_prescription
from .models import (
    Medication,
    Prescription,
    PrescriptionItem,
    StockBatch,
)
from functools import wraps

from django.http import HttpResponseForbidden
from core.department_access import department_required

def pharmacy_required(view_func):
    @wraps(view_func)
    @department_required("PHARM")
    def wrapped(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        from clinic.departments.models import DepartmentMembership

        has_access = DepartmentMembership.objects.filter(
            user=request.user,
            department__code="PHARM",
            department__is_active=True,
            organization__is_active=True,
            is_active=True,
        ).exists()

        if not has_access:
            return HttpResponseForbidden(
                "You do not have permission to access the pharmacy workspace."
            )

        return view_func(request, *args, **kwargs)

    return wrapped

@department_required("PHARM")
@transaction.atomic
def create_prescription(request, consultation_id):
    consultation = get_object_or_404(
        Consultation.objects.select_related(
            "encounter",
            "encounter__patient",
            "doctor",
        ),
        id=consultation_id,
    )

    if consultation.doctor_id != request.user.id:
        messages.error(
            request,
            "Only the doctor assigned to this consultation can create a prescription.",
        )
        return redirect(
            "consultations:detail",
            consultation_id=consultation.id,
        )

    # Find an existing open prescription for this consultation.
    prescription = (
        Prescription.objects
        .filter(
            consultation=consultation,
            status=Prescription.Status.OPEN,
        )
        .order_by("-created_at")
        .first()
    )

    # Create one only if this consultation does not already have an open one.
    if not prescription:
        prescription = Prescription.objects.create(
            consultation=consultation,
            patient=consultation.encounter.patient,
            prescribed_by=request.user,
        )

    if request.method == "POST":

        medication_id = request.POST.get("medication")
        dose = request.POST.get("dose", "").strip()
        frequency = request.POST.get("frequency", "").strip()
        duration = request.POST.get("duration", "").strip()
        quantity = request.POST.get("quantity", "").strip()
        instructions = request.POST.get("instructions", "").strip()

        if not medication_id:
            messages.error(request, "Please select a medication.")
            return redirect(
                "pharmacy:create_prescription",
                consultation_id=consultation.id,
            )

        medication = get_object_or_404(
            Medication,
            id=medication_id,
            is_active=True,
        )

        if not dose or not frequency or not duration or not quantity:
            messages.error(
                request,
                "Medication, dose, frequency, duration, and quantity are required.",
            )
            return redirect(
                "pharmacy:create_prescription",
                consultation_id=consultation.id,
            )

        try:
            quantity = int(quantity)

            if quantity <= 0:
                raise ValueError

        except ValueError:
            messages.error(
                request,
                "Quantity must be a positive whole number.",
            )
            return redirect(
                "pharmacy:create_prescription",
                consultation_id=consultation.id,
            )

        PrescriptionItem.objects.create(
            prescription=prescription,
            medication=medication,
            dose=dose,
            frequency=frequency,
            duration=duration,
            quantity=quantity,
            instructions=instructions,
        )

        messages.success(
            request,
            f"{medication} added to prescription {prescription.prescription_id}.",
        )

        return redirect(
            "pharmacy:create_prescription",
            consultation_id=consultation.id,
        )

    medications = Medication.objects.filter(
        is_active=True
    ).order_by(
        "name",
        "strength",
    )

    items = (
        prescription.items
        .select_related("medication")
        .order_by("id")
    )

    return render(
        request,
        "pharmacy/create_prescription.html",
        {
            "consultation": consultation,
            "patient": consultation.encounter.patient,
            "prescription": prescription,
            "items": items,
            "medications": medications,
        },
    )

@department_required("PHARM")
@transaction.atomic
def finalize_prescription(request, prescription_id):
    if request.method != "POST":
        return redirect("consultations:detail", consultation_id=1)

    prescription = get_object_or_404(
        Prescription.objects.select_related(
            "consultation",
            "consultation__encounter",
            "consultation__encounter__patient",
            "prescribed_by",
        ),
        id=prescription_id,
    )

    if prescription.prescribed_by_id != request.user.id:
        messages.error(
            request,
            "Only the doctor who created this prescription can finalize it.",
        )
        return redirect(
            "consultations:detail",
            consultation_id=prescription.consultation.id,
        )

    if prescription.status != Prescription.Status.OPEN:
        messages.error(
            request,
            "This prescription has already been finalized or cancelled.",
        )
        return redirect(
            "consultations:detail",
            consultation_id=prescription.consultation.id,
        )

    if not prescription.items.exists():
        messages.error(
            request,
            "A prescription must contain at least one medication before it can be finalized.",
        )
        return redirect(
            "pharmacy:create_prescription",
            consultation_id=prescription.consultation.id,
        )

    prescription.status = Prescription.Status.COMPLETED
    prescription.save(update_fields=["status", "updated_at"])

    messages.success(
        request,
        f"Prescription {prescription.prescription_id} has been finalized and is ready for pharmacy.",
    )

    return redirect(
        "consultations:detail",
        consultation_id=prescription.consultation.id,
    )

@pharmacy_required
def pharmacy_queue(request):
    """
    Display finalized prescriptions that are ready for pharmacy processing.
    """

    prescriptions = (
        Prescription.objects
        .filter(status=Prescription.Status.COMPLETED)
        .select_related(
            "patient",
            "consultation",
            "prescribed_by",
        )
        .prefetch_related(
            "items__medication",
        )
        .order_by("-created_at")
    )

    return render(
        request,
        "pharmacy/pharmacy_queue.html",
        {
            "prescriptions": prescriptions,
        },
    )

@pharmacy_required
def prescription_detail(request, prescription_id):
    prescription = get_object_or_404(
        Prescription.objects
        .select_related(
            "patient",
            "consultation",
            "prescribed_by",
        )
        .prefetch_related(
            "items__medication",
        ),
        id=prescription_id,
    )

    items = prescription.items.select_related(
        "medication",
    ).order_by("id")

    # Get all active stock batches for the medications
    # in this prescription.
    medication_ids = items.values_list(
        "medication_id",
        flat=True,
    )

    stock_batches = (
        StockBatch.objects
        .filter(
            medication_id__in=medication_ids,
            is_active=True,
        )
        .order_by(
            "medication_id",
            "expiry_date",
        )
    )

    return render(
        request,
        "pharmacy/prescription_detail.html",
        {
            "prescription": prescription,
            "items": items,
            "stock_batches": stock_batches,
        },
    )

@department_required("PHARM")
@transaction.atomic
def dispense_prescription_view(request, prescription_id):
    if request.method != "POST":
        return redirect(
            "pharmacy:prescription_detail",
            prescription_id=prescription_id,
        )

    prescription = get_object_or_404(
        Prescription.objects.select_related(
            "patient",
            "consultation",
            "prescribed_by",
        ),
        id=prescription_id,
    )

    try:
        movements = dispense_prescription(
            prescription=prescription,
            performed_by=request.user,
        )

    except ValidationError as exc:
        messages.error(
            request,
            str(exc),
        )

        return redirect(
            "pharmacy:prescription_detail",
            prescription_id=prescription.id,
        )

    messages.success(
        request,
        (
            f"Prescription {prescription.prescription_id} "
            f"was dispensed successfully. "
            f"{len(movements)} stock movement(s) recorded."
        ),
    )

    return redirect(
        "pharmacy:prescription_detail",
        prescription_id=prescription.id,
    )