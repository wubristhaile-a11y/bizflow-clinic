from django.urls import path

from . import views


app_name = "triage"

urlpatterns = [
    path(
        "",
        views.triage_queue,
        name="queue",
    ),

    path(
        "encounter/<int:encounter_id>/",
        views.triage_detail,
        name="detail",
    ),
]