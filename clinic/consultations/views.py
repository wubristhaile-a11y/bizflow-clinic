from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from clinic.billing.models import Invoice, InvoiceItem
from clinic.encounters.models import Encounter
from clinic.laboratory.services import review_lab_result
from clinic.orders.models import ClinicalOrder
from clinic.services.models import Service
from core.department_access import department_required
from .forms import InvestigationOrderForm
from .models import Consultation

@department_required("CONS")
def consultation_queue(request):
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
            ],
            triage__isnull=False,
        )
        .order_by("created_at")
    )

    return render(
        request,
        "consultations/queue.html",
        {
            "encounters": encounters,
        },
    )
@department_required("CONS")
def consultation_detail(request, consultation_id):
    consultation = get_object_or_404(
        Consultation.objects.select_related(
            "encounter",
            "encounter__patient",
            "encounter__triage",
            "doctor",
        ),
        id=consultation_id,
    )

    patient = consultation.encounter.patient
    triage = getattr(consultation.encounter, "triage", None)

    investigations = (
        consultation.clinical_orders
        .select_related(
            "service",
            "service__department",
            "ordered_by",
        )
        .prefetch_related("lab_result")
        .order_by("-ordered_at")
    )
    prescriptions = (
        consultation.prescriptions
        .select_related("prescribed_by")
        .prefetch_related("items__medication")
        .order_by("-created_at")
    )
    form = InvestigationOrderForm()

    context = {
        "consultation": consultation,
        "patient": patient,
        "encounter": consultation.encounter,
        "triage": triage,
        "investigations": investigations,
        "prescriptions": prescriptions,
        "investigation_form": form,
    }

    return render(
        request,
        "consultations/detail.html",
        context,
    )


@department_required("CONS")
@transaction.atomic
def save_consultation(request, consultation_id):
    if request.method != "POST":
        return redirect(
            "consultations:detail",
            consultation_id=consultation_id,
        )

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
            "Only the doctor assigned to this consultation can update it.",
        )

        return redirect(
            "consultations:detail",
            consultation_id=consultation.id,
        )

    consultation.chief_complaint = request.POST.get(
        "chief_complaint",
        "",
    ).strip()

    consultation.history_of_present_illness = request.POST.get(
        "history_of_present_illness",
        "",
    ).strip()

    consultation.medical_history = request.POST.get(
        "medical_history",
        "",
    ).strip()

    consultation.physical_examination = request.POST.get(
        "physical_examination",
        "",
    ).strip()

    consultation.assessment = request.POST.get(
        "assessment",
        "",
    ).strip()

    consultation.diagnosis = request.POST.get(
        "diagnosis",
        "",
    ).strip()

    consultation.treatment_plan = request.POST.get(
        "treatment_plan",
        "",
    ).strip()

    consultation.save()

    messages.success(
        request,
        f"Consultation {consultation.consultation_id} saved successfully.",
    )

    return redirect(
        "consultations:detail",
        consultation_id=consultation.id,
    )


@department_required("CONS")
@transaction.atomic
def order_investigation(request, consultation_id):

    if request.method != "POST":
        return redirect(
            "consultations:detail",
            consultation_id=consultation_id,
        )

    consultation = get_object_or_404(
        Consultation.objects.select_related(
            "encounter",
            "encounter__patient",
        ),
        id=consultation_id,
    )

    if consultation.doctor_id != request.user.id:
        messages.error(
            request,
            "Only the doctor assigned to this consultation can "
            "order investigations.",
        )

        return redirect(
            "consultations:detail",
            consultation_id=consultation.id,
        )

    form = InvestigationOrderForm(request.POST)

    if not form.is_valid():
        messages.error(
            request,
            "Please correct the investigation order form.",
        )

        return redirect(
            "consultations:detail",
            consultation_id=consultation.id,
        )

    service = form.cleaned_data["service"]
    clinical_notes = form.cleaned_data["clinical_notes"]

    order = ClinicalOrder.objects.create(
        encounter=consultation.encounter,
        consultation=consultation,
        service=service,
        ordered_by=request.user,
        status=ClinicalOrder.Status.AWAITING_PAYMENT,
        price=service.price,
        clinical_notes=clinical_notes,
    )

    invoice = Invoice.objects.create(
        encounter=consultation.encounter,
        created_by=request.user,
    )

    InvoiceItem.objects.create(
        invoice=invoice,
        clinical_order=order,
        description=service.name,
        quantity=1,
        unit_price=service.price,
    )

    messages.success(
        request,
        (
            f"{service.name} has been ordered successfully. "
            f"Order {order.order_id} is now awaiting payment."
        ),
    )

    return redirect(
        "consultations:detail",
        consultation_id=consultation.id,
    )


@department_required("CONS")
def review_result(request, order_id):

    if request.method != "POST":
        messages.error(
            request,
            "Invalid request.",
        )

        return redirect(
            "encounters:detail",
            encounter_id=1,
        )

    order = get_object_or_404(
        ClinicalOrder.objects.select_related(
            "consultation",
            "encounter",
            "encounter__patient",
            "service",
            "service__department",
        ),
        id=order_id,
    )

    try:
        lab_result, updated_order = review_lab_result(
            order_id=order.id,
            reviewed_by=request.user,
        )

        messages.success(
            request,
            (
                f"{order.order_id} laboratory result has been "
                "reviewed successfully."
            ),
        )

        return redirect(
            "consultations:detail",
            consultation_id=order.consultation.id,
        )

    except Exception as exc:

        messages.error(
            request,
            str(exc),
        )

        return redirect(
            "consultations:detail",
            consultation_id=order.consultation.id,
        )


@department_required("CONS")
@transaction.atomic
def start_consultation(request, encounter_id):

    if request.method != "POST":
        return redirect(
            "encounters:detail",
            encounter_id=encounter_id,
        )

    encounter = get_object_or_404(
        Encounter.objects.select_related("patient"),
        id=encounter_id,
    )

    if hasattr(encounter, "consultation"):
        return redirect(
            "consultations:detail",
            consultation_id=encounter.consultation.id,
        )

    consultation = Consultation.objects.create(
        encounter=encounter,
        doctor=request.user,
        status=Consultation.Status.OPEN,
    )

    if encounter.status == Encounter.Status.OPEN:
        encounter.status = Encounter.Status.IN_PROGRESS
        encounter.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

    messages.success(
        request,
        (
            f"Consultation {consultation.consultation_id} "
            "started successfully."
        ),
    )

    return redirect(
        "consultations:detail",
        consultation_id=consultation.id,
    )