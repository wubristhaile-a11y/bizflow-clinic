from django.urls import path

from . import views


app_name = "patients"

urlpatterns = [
    path(
        "new/",
        views.create_patient,
        name="create",
    ),

    path(
        "",
        views.patient_list,
        name="list",
    ),

    path(
        "<int:patient_id>/",
        views.patient_detail,
        name="detail",
    ),
]