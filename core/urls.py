from django.urls import path

from . import views
from . import department_views


app_name = "core"


urlpatterns = [
    path(
        "",
        views.home,
        name="home",
    ),

    path(
        "reception/",
        department_views.reception_workspace,
        name="reception_workspace",
    ),

    path(
        "departments/<str:department_code>/",
        department_views.department_workspace,
        name="department_workspace",
    ),
]