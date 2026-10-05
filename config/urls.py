from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    # ==========================================
    # WUB TECH SOLUTIONS PUBLIC HOME
    # ==========================================
    path("", include("core.urls")),

    # ==========================================
    # CLINIC PRODUCT HOME
    # ==========================================
    path("clinic/", include("clinic.urls")),

    # ==========================================
    # ADMIN
    # ==========================================
    path("admin/", admin.site.urls),

    # ==========================================
    # CLINIC MODULES
    # ==========================================
    path(
        "laboratory/",
        include("clinic.laboratory.urls"),
    ),
    path(
        "consultations/",
        include("clinic.consultations.urls"),
    ),
    path(
        "billing/",
        include("clinic.billing.urls"),
    ),
    path(
        "patients/",
        include("clinic.patients.urls"),
    ),
    path(
        "encounters/",
        include("clinic.encounters.urls"),
    ),
    path(
        "triage/",
        include("clinic.triage.urls"),
    ),
    path(
        "pharmacy/",
        include("clinic.pharmacy.urls"),
    ),

    # ==========================================
    # ACCOUNTS
    # ==========================================
    path(
        "accounts/",
        include("core.accounts.urls"),
    ),

    # ==========================================
    # SCHOOL
    # ==========================================
    path(
        "school/",
        include("school.urls"),
    ),
]