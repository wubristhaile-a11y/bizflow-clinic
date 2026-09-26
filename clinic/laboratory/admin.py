from django.contrib import admin

from .models import LabResult


@admin.register(LabResult)
class LabResultAdmin(admin.ModelAdmin):
    list_display = (
        "result_id",
        "clinical_order",
        "performed_by",
        "status",
        "performed_at",
        "created_at",
    )

    list_filter = (
        "status",
        "performed_at",
        "created_at",
    )

    search_fields = (
        "result_id",
        "clinical_order__order_id",
        "clinical_order__encounter__patient__patient_id",
        "clinical_order__encounter__patient__full_name",
        "clinical_order__service__name",
    )

    readonly_fields = (
        "result_id",
        "clinical_order",
        "performed_by",
        "result",
        "notes",
        "status",
        "performed_at",
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False