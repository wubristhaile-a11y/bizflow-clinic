from django.urls import path

from . import views


app_name = "pharmacy"

urlpatterns = [
    path(
        "consultation/<int:consultation_id>/new/",
        views.create_prescription,
        name="create_prescription",
    ),
    path(
        "prescriptions/<int:prescription_id>/finalize/",
        views.finalize_prescription,
        name="finalize_prescription",
    ),
    path(
        "",
        views.pharmacy_queue,
        name="queue",
    ),
    path(
        "prescriptions/<int:prescription_id>/",
        views.prescription_detail,
        name="prescription_detail",
    ),
    path(
        "prescriptions/<int:prescription_id>/dispense/",
        views.dispense_prescription_view,
        name="dispense_prescription",
    ),
]