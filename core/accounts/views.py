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
    Route the authenticated user to the appropriate department workspace.
    """

    from clinic.departments.models import DepartmentMembership

    memberships = list(
        DepartmentMembership.objects
        .filter(
            user=request.user,
            is_active=True,
            organization__is_active=True,
        )
        .select_related(
            "department",
            "organization",
        )
        .order_by("department__name")
    )

    if not memberships:
        messages.warning(
            request,
            "Your account is active, but no department access has been assigned.",
        )
        return redirect("clinic:home")

    requested_department = request.session.pop(
        "requested_department",
        "",
    ).strip().upper()

    selected_membership = None

    if requested_department:
        for membership in memberships:
            if membership.department.code.upper() == requested_department:
                selected_membership = membership
                break

    if selected_membership is None:
        selected_membership = memberships[0]

    department_code = selected_membership.department.code.upper()

    department_routes = {
        "PHARM": "pharmacy:queue",
        "LAB": "laboratory:queue",
        "RECEPTION": "core:reception_workspace",
        "TRIAGE": "triage:queue",
        "CONS": "consultations:queue",
        "BILLING": "billing:invoice_queue",
        "SCHOOL": "school:dashboard",
    }

    route_name = department_routes.get(department_code)

    # Dedicated department workspace.
    if route_name:
        return redirect(route_name)

    # Generic workspace for departments that do not yet
    # have their own specialized module.
    return redirect(
        "core:department_workspace",
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

    return redirect("clinic:home")