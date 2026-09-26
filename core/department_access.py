from functools import wraps

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from clinic.departments.models import DepartmentMembership


def department_required(department_code):
    """
    Require the authenticated user to have active access
    to the requested department.
    """

    def decorator(view_func):

        @wraps(view_func)
        @login_required
        def wrapped(request, *args, **kwargs):

            has_access = (
                DepartmentMembership.objects
                .filter(
                    user=request.user,
                    department__code=department_code,
                    department__is_active=True,
                    organization__is_active=True,
                    is_active=True,
                )
                .exists()
            )

            if not has_access:
                return HttpResponseForbidden(
                    "You do not have permission to access this department."
                )

            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator