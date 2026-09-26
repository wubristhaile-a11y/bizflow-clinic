from django.urls import path

from . import views
from .department_views import (
    department_workspace,
    reception_workspace,
)


urlpatterns = [
    path(
        "",
        views.clinic_home,
        name="clinic_home",
    ),

    path(
        "workspace/reception/",
        reception_workspace,
        name="reception_workspace",
    ),

    path(
        "workspace/<str:department_code>/",
        department_workspace,
        name="department_workspace",
    ),
]