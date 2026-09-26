from django.contrib import admin

from .models import Encounter


@admin.register(Encounter)
class EncounterAdmin(admin.ModelAdmin):
    list_display = (
        "encounter_id",
        "patient",
        "status",
        "attended_by",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "encounter_id",
        "patient__patient_id",
        "patient__full_name",
        "patient__phone",
    )

    readonly_fields = (
        "encounter_id",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )