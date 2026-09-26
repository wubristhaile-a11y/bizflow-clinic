from django.contrib import admin

from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        "patient_id",
        "full_name",
        "age",
        "sex",
        "phone",
        "is_active",
        "created_at",
    )

    list_filter = (
        "sex",
        "is_active",
    )

    search_fields = (
        "patient_id",
        "full_name",
        "phone",
    )

    readonly_fields = (
        "patient_id",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )