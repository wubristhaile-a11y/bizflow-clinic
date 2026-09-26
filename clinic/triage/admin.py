
from django.contrib import admin

from .models import TriageRecord


@admin.register(TriageRecord)
class TriageRecordAdmin(admin.ModelAdmin):
    list_display = (
        "encounter",
        "systolic_bp",
        "diastolic_bp",
        "temperature",
        "pulse",
        "weight",
        "blood_sugar",
        "recorded_by",
        "recorded_at",
    )

    search_fields = (
        "encounter__encounter_id",
        "encounter__patient__patient_id",
        "encounter__patient__full_name",
        "encounter__patient__phone",
    )

    list_filter = ("recorded_at",)

    readonly_fields = (
        "recorded_at",
        "updated_at",
    )

    ordering = ("-recorded_at",)