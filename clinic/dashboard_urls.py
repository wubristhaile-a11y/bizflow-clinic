from django.urls import path

from .dashboard import dashboard


app_name = "clinic"


urlpatterns = [
    path("", dashboard, name="dashboard"),
]