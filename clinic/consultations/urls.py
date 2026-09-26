from django.urls import path

from . import views


app_name = "consultations"


urlpatterns = [
    path(
        "",
        views.consultation_queue,
        name="queue",
    ),

    path(
        "<int:consultation_id>/",
        views.consultation_detail,
        name="detail",
    ),

    path(
        "<int:consultation_id>/save/",
        views.save_consultation,
        name="save",
    ),

    path(
        "results/<int:order_id>/review/",
        views.review_result,
        name="review_result",
    ),

    path(
        "<int:consultation_id>/order-investigation/",
        views.order_investigation,
        name="order_investigation",
    ),

    path(
        "encounter/<int:encounter_id>/start/",
        views.start_consultation,
        name="start_consultation",
    ),
]