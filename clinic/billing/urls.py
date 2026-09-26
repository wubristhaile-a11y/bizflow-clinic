from django.urls import path

from . import views


app_name = "billing"

urlpatterns = [
    path("", views.invoice_queue, name="invoice_queue"),
    path(
        "invoices/<int:invoice_id>/pay/",
        views.receive_payment,
        name="receive_payment",
    ),
]