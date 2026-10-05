from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.utils import timezone

from clinic.departments.models import DepartmentMembership
from clinic.encounters.models import Encounter
from clinic.patients.models import Patient
from core.department_access import department_required

@login_required
def department_workspace(request, department_code):
    
    department_code = department_code.upper()

    specialized_routes = {
        "PHARM": "pharmacy:queue",
        "LAB": "laboratory:queue",
        "CONS": "consultations:queue",
        "RECEPTION": "core:reception_workspace",
        "TRIAGE": "triage:queue",
        "BILLING": "billing:invoice_queue",
        "SCHOOL": "school:dashboard",
    }

    route_name = specialized_routes.get(department_code)

    if route_name:
        return redirect(route_name)
        
    """
    Generic department workspace.
    """
    membership = (
        DepartmentMembership.objects
        .filter(
            user=request.user,
            department__code=department_code,
            department__is_active=True,
            organization__is_active=True,
            is_active=True,
        )
        .select_related(
            "organization",
            "department",
        )
        .first()
    )

    if membership is None:
        return HttpResponseForbidden(
            "You do not have permission to access this department."
        )

    return render(
        request,
        "departments/workspace.html",
        {
            "membership": membership,
            "department": membership.department,
        },
    )


@department_required("RECEPTION")
def reception_workspace(request):
    """
    Reception department dashboard.
    """

    membership = (
        DepartmentMembership.objects
        .filter(
            user=request.user,
            department__code="RECEPTION",
            department__is_active=True,
            organization__is_active=True,
            is_active=True,
        )
        .select_related(
            "organization",
            "department",
        )
        .first()
    )

    if membership is None:
        return HttpResponseForbidden(
            "You do not have permission to access Reception."
        )

    today = timezone.localdate()

    encounters = (
        Encounter.objects
        .select_related("patient", "attended_by")
        .order_by("-created_at")[:20]
    )

    patient_count = Patient.objects.filter(
        is_active=True
    ).count()

    today_encounters = Encounter.objects.filter(
        created_at__date=today
    ).count()

    waiting_count = Encounter.objects.filter(
        status__in=[
            Encounter.Status.OPEN,
            Encounter.Status.IN_PROGRESS,
        ]
    ).count()

    return render(
        request,
        "departments/reception.html",
        {
            "membership": membership,
            "department": membership.department,
            "encounters": encounters,
            "patient_count": patient_count,
            "today_encounters": today_encounters,
            "waiting_count": waiting_count,
        },
    )