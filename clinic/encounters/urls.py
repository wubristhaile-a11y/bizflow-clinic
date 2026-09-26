from django.urls import path

from . import views


app_name = "encounters"

urlpatterns = [
    path(
        "",
        views.encounter_list,
        name="list",
    ),

    path(
        "patient/<int:patient_id>/new/",
        views.create_encounter,
        name="create",
    ),

    path(
        "<int:encounter_id>/",
        views.encounter_detail,
        name="detail",
    ),
]