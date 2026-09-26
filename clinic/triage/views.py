from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from clinic.encounters.models import Encounter
from core.department_access import department_required
from .models import TriageRecord

@department_required("TRIAGE")
def triage_queue(request):
    encounters = (
        Encounter.objects
        .select_related(
            "patient",
            "attended_by",
            "triage",
        )
        .filter(
            status__in=[
                Encounter.Status.OPEN,
                Encounter.Status.IN_PROGRESS,
            ]
        )
        .order_by("created_at")
    )

    return render(
        request,
        "triage/queue.html",
        {
            "encounters": encounters,
        },
    )
@department_required("TRIAGE")
def triage_detail(request, encounter_id):
    encounter = get_object_or_404(
        Encounter.objects.select_related(
            "patient",
            "attended_by",
        ),
        id=encounter_id,
    )

    triage = getattr(encounter, "triage", None)

    if request.method == "POST":
        systolic_bp = request.POST.get("systolic_bp", "").strip()
        diastolic_bp = request.POST.get("diastolic_bp", "").strip()
        temperature = request.POST.get("temperature", "").strip()
        pulse = request.POST.get("pulse", "").strip()
        weight = request.POST.get("weight", "").strip()
        blood_sugar = request.POST.get("blood_sugar", "").strip()
        notes = request.POST.get("notes", "").strip()

        if triage:
            triage.systolic_bp = systolic_bp or None
            triage.diastolic_bp = diastolic_bp or None
            triage.temperature = temperature or None
            triage.pulse = pulse or None
            triage.weight = weight or None
            triage.blood_sugar = blood_sugar or None
            triage.notes = notes
            triage.recorded_by = request.user
            triage.save()

            messages.success(
                request,
                "Triage information updated successfully.",
            )

        else:
            TriageRecord.objects.create(
                encounter=encounter,
                systolic_bp=systolic_bp or None,
                diastolic_bp=diastolic_bp or None,
                temperature=temperature or None,
                pulse=pulse or None,
                weight=weight or None,
                blood_sugar=blood_sugar or None,
                notes=notes,
                recorded_by=request.user,
            )

            messages.success(
                request,
                "Triage information recorded successfully.",
            )

        if encounter.status == Encounter.Status.OPEN:
            encounter.status = Encounter.Status.IN_PROGRESS
            encounter.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

        return redirect(
            "encounters:detail",
            encounter_id=encounter.id,
        )

    return render(
        request,
        "triage/triage_detail.html",
        {
            "encounter": encounter,
            "patient": encounter.patient,
            "triage": triage,
        },
    )