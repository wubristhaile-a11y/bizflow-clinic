from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from clinic.orders.models import ClinicalOrder
from core.department_access import department_required
from .forms import LabResultForm
from .services import (
    complete_lab_result,
    start_lab_order,
)


@department_required("LAB")
def laboratory_queue(request):
    """
    Main laboratory work queue.
    """

    base_orders = (
        ClinicalOrder.objects
        .filter(service__department__code="LAB")
        .select_related(
            "encounter__patient",
            "service",
            "service__department",
            "ordered_by",
        )
        .order_by("-ordered_at")
    )

    waiting_orders = base_orders.filter(
        status=ClinicalOrder.Status.PAID
    )

    in_progress_orders = base_orders.filter(
        status=ClinicalOrder.Status.IN_PROGRESS
    )

    result_available_orders = base_orders.filter(
        status=ClinicalOrder.Status.RESULT_AVAILABLE
    )

    reviewed_orders = base_orders.filter(
        status=ClinicalOrder.Status.DOCTOR_REVIEWED
    )

    context = {
        "waiting_orders": waiting_orders,
        "in_progress_orders": in_progress_orders,
        "result_available_orders": result_available_orders,
        "reviewed_orders": reviewed_orders,
    }

    return render(
        request,
        "laboratory/queue.html",
        context,
    )


@department_required("LAB")
def start_order(request, order_id):
    """
    Start a paid laboratory order.
    """

    if request.method != "POST":
        return redirect("laboratory:queue")

    order = get_object_or_404(
        ClinicalOrder,
        id=order_id,
    )

    try:
        start_lab_order(order.id)

        messages.success(
            request,
            f"{order.order_id} has been moved to In Progress.",
        )

    except Exception as exc:
        messages.error(
            request,
            str(exc),
        )

    return redirect("laboratory:queue")


@department_required("LAB")
def enter_result(request, order_id):
    """
    Enter and complete a laboratory result.
    """

    order = get_object_or_404(
        ClinicalOrder.objects.select_related(
            "encounter__patient",
            "service",
            "service__department",
        ),
        id=order_id,
    )

    if order.service.department.code != "LAB":
        messages.error(
            request,
            "This order does not belong to the Laboratory.",
        )

        return redirect("laboratory:queue")

    if order.status != ClinicalOrder.Status.IN_PROGRESS:
        messages.error(
            request,
            "Only laboratory orders currently in progress "
            "can receive a result.",
        )

        return redirect("laboratory:queue")

    if request.method == "POST":

        form = LabResultForm(request.POST)

        if form.is_valid():

            try:

                complete_lab_result(
                    order_id=order.id,
                    performed_by=request.user,
                    result=form.cleaned_data["result"],
                    notes=form.cleaned_data["notes"],
                )

                messages.success(
                    request,
                    f"Result for {order.order_id} "
                    f"has been completed.",
                )

                return redirect(
                    "laboratory:queue"
                )

            except Exception as exc:

                messages.error(
                    request,
                    str(exc),
                )

    else:

        form = LabResultForm()

    context = {
        "order": order,
        "form": form,
    }

    return render(
        request,
        "laboratory/enter_result.html",
        context,
    )