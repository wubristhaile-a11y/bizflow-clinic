from django.urls import path

from . import views


app_name = "laboratory"


urlpatterns = [
    path(
        "",
        views.laboratory_queue,
        name="queue",
    ),

    path(
        "orders/<int:order_id>/start/",
        views.start_order,
        name="start_order",
    ),

    path(
        "orders/<int:order_id>/result/",
        views.enter_result,
        name="enter_result",
    ),
]