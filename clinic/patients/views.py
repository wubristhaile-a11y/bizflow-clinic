from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PatientForm
from .models import Patient


@login_required
def patient_list(request):
    query = request.GET.get("q", "").strip()

    patients = Patient.objects.filter(
        is_active=True
    ).order_by("full_name")

    if query:
        patients = patients.filter(
            Q(patient_id__icontains=query)
            | Q(full_name__icontains=query)
            | Q(phone__icontains=query)
        )

    return render(
        request,
        "patients/patient_list.html",
        {
            "patients": patients,
            "query": query,
        },
    )


@login_required
def patient_detail(request, patient_id):
    patient = get_object_or_404(
        Patient.objects.prefetch_related(
            "encounters",
        ),
        id=patient_id,
    )

    encounters = (
        patient.encounters
        .select_related(
            "attended_by",
            "triage",
            "consultation",
            "consultation__doctor",
        )
        .prefetch_related(
            "clinical_orders",
            "clinical_orders__service",
            "clinical_orders__service__department",
            "clinical_orders__lab_result",
        )
        .order_by("-created_at")
    )

    return render(
        request,
        "patients/patient_detail.html",
        {
            "patient": patient,
            "encounters": encounters,
        },
    )


@login_required
def create_patient(request):
    if request.method == "POST":
        form = PatientForm(request.POST)

        if form.is_valid():
            patient = form.save()

            messages.success(
                request,
                f"Patient {patient.patient_id} registered successfully.",
            )

            return redirect(
                "patients:detail",
                patient_id=patient.id,
            )
    else:
        form = PatientForm()

    return render(
        request,
        "patients/create.html",
        {
            "form": form,
        },
    )