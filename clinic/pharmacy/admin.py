from django.contrib import admin

from .models import (
    Medication,
    Prescription,
    PrescriptionItem,
    StockBatch,
    StockMovement,
)


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "generic_name",
        "strength",
        "dosage_form",
        "unit",
        "is_active",
    )

    list_filter = (
        "dosage_form",
        "is_active",
    )

    search_fields = (
        "name",
        "generic_name",
        "strength",
    )

    ordering = (
        "name",
        "strength",
    )


class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 1


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = (
        "prescription_id",
        "patient",
        "consultation",
        "prescribed_by",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "prescription_id",
        "patient__full_name",
        "patient__patient_id",
    )

    readonly_fields = (
        "prescription_id",
        "created_at",
        "updated_at",
    )

    inlines = (
        PrescriptionItemInline,
    )

    ordering = (
        "-created_at",
    )
@admin.register(StockBatch)
class StockBatchAdmin(admin.ModelAdmin):

    list_display = (
        "medication",
        "batch_number",
        "expiry_date",
        "quantity",
        "purchase_price",
        "selling_price",
        "is_active",
    )

    list_filter = (
        "is_active",
        "expiry_date",
    )

    search_fields = (
        "medication__name",
        "medication__generic_name",
        "batch_number",
    )

    ordering = (
        "expiry_date",
        "medication__name",
    )
    
@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = (
        "medication",
        "stock_batch",
        "movement_type",
        "quantity",
        "reference",
        "performed_by",
        "created_at",
    )

    list_filter = (
        "movement_type",
        "created_at",
    )

    search_fields = (
        "medication__name",
        "medication__generic_name",
        "stock_batch__batch_number",
        "reference",
        "performed_by__username",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "created_at",
    )