from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from clinic.patients.models import Patient

from .models import Encounter

@login_required
def encounter_list(request):
    encounters = (
        Encounter.objects
        .select_related(
            "patient",
            "attended_by",
        )
        .order_by("-created_at")
    )

    return render(
        request,
        "encounters/encounter_list.html",
        {
            "encounters": encounters,
        },
    )
@login_required
def create_encounter(request, patient_id):
    patient = get_object_or_404(
        Patient,
        id=patient_id,
        is_active=True,
    )

    if request.method == "POST":
        visit_reason = request.POST.get("visit_reason", "").strip()

        encounter = Encounter.objects.create(
            patient=patient,
            attended_by=request.user,
            status=Encounter.Status.OPEN,
            visit_reason=visit_reason,
        )

        messages.success(
            request,
            f"Encounter {encounter.encounter_id} created successfully.",
        )

        return redirect(
            "patients:detail",
            patient_id=patient.id,
        )

    return render(
        request,
        "encounters/create_encounter.html",
        {
            "patient": patient,
        },
    )
@login_required
def encounter_detail(request, encounter_id):
    encounter = get_object_or_404(
    Encounter.objects.select_related(
    "patient",
    "attended_by",
    ).prefetch_related(
    "clinical_orders",
    "clinical_orders__service",
    "clinical_orders__service__department",
    ),
    id=encounter_id,
    )


    return render(
        request,
        "encounters/encounter_detail.html",
        {
            "encounter": encounter,
            "patient": encounter.patient,
        },
    )

