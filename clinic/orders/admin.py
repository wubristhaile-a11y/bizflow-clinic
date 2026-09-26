from django.contrib import admin

from .models import ClinicalOrder


@admin.register(ClinicalOrder)
class ClinicalOrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_id",
        "encounter",
        "service",
        "ordered_by",
        "status",
        "price",
        "ordered_at",
        "updated_at",
    )

    list_filter = (
        "status",
        "service__department",
        "ordered_at",
    )

    search_fields = (
        "order_id",
        "encounter__encounter_id",
        "encounter__patient__patient_id",
        "encounter__patient__full_name",
        "service__name",
        "service__code",
        "ordered_by__username",
    )

    readonly_fields = (
        "order_id",
        "ordered_at",
        "updated_at",
    )

    ordering = ("-ordered_at",)