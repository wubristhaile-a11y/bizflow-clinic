from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


def login_view(request):
    requested_department = request.GET.get("department", "").strip().lower()

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:
            if not user.is_active:
                messages.error(
                    request,
                    "Your account is inactive. Please contact an administrator.",
                )
                return render(
                    request,
                    "accounts/login.html",
                    {
                        "requested_department": requested_department,
                    },
                )

            login(request, user)

            if requested_department:
                request.session["requested_department"] = requested_department

            return redirect("accounts:post_login")

        messages.error(
            request,
            "Invalid username or password.",
        )

    return render(
        request,
        "accounts/login.html",
        {
            "requested_department": requested_department,
        },
    )
    
@login_required
def post_login(request):
    """
    Route the authenticated user to the requested department workspace.
    """

    from clinic.departments.models import DepartmentMembership

    memberships = list(
        DepartmentMembership.objects
        .filter(
            user=request.user,
            is_active=True,
            organization__is_active=True,
            department__is_active=True,
        )
        .select_related(
            "organization",
            "department",
        )
        .order_by("department__name")
    )

    if not memberships:
        messages.warning(
            request,
            "Your account is not assigned to an active department.",
        )

        return render(
            request,
            "accounts/post_login.html",
        )

    requested_department = request.session.pop(
        "requested_department",
        None,
    )

    requested_department_codes = {
        "reception": "RECEPTION",
        "triage": "TRIAGE",
        "doctor": "CONS",
        "laboratory": "LAB",
        "imaging": "IMG",
        "pharmacy": "PHARM",
        "billing": "BILLING",
        "admin": "ADMIN",
    }

    if requested_department:
        requested_department = requested_department_codes.get(
            requested_department.lower(),
            requested_department.upper(),
        )

    selected_membership = None

    # If a department was explicitly requested,
    # find that department in the user's memberships.
    if requested_department:

        for membership in memberships:

            if membership.department.code == requested_department:

                selected_membership = membership
                break

    # If no department was requested, use the first
    # available department.
    if selected_membership is None:
        selected_membership = memberships[0]

    department_code = selected_membership.department.code

    # Existing functional workspaces.
    department_routes = {
        "PHARM": "pharmacy:queue",
        "LAB": "laboratory:queue",
        "RECEPTION": "reception_workspace",
        "TRIAGE": "triage:queue",
        "CONS": "consultations:queue",
        "BILLING": "billing:queue",
    }

    route_name = department_routes.get(department_code)

    if route_name:
        return redirect(route_name)

    # Departments whose full workspace is still being built.
    return redirect(
        "department_workspace",
        department_code=department_code,
    )
@login_required
def logout_view(request):
    """
    Log the staff member out and return to the clinic landing page.
    """

    logout(request)

    messages.success(
        request,
        "You have been signed out.",
    )

    return redirect("clinic_home")