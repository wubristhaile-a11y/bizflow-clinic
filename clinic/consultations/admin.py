from django.contrib import admin

from .models import Consultation


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = (
        "consultation_id",
        "encounter",
        "doctor",
        "status",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "consultation_id",
        "encounter__encounter_id",
        "encounter__patient__patient_id",
        "encounter__patient__full_name",
        "encounter__patient__phone",
        "doctor__username",
    )

    readonly_fields = (
        "consultation_id",
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)