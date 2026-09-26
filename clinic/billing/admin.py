
from django import forms
from django.contrib import admin

from .models import Invoice, InvoiceItem, Payment
from .services import record_payment

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_id",
        "encounter",
        "status",
        "created_by",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "invoice_id",
        "encounter__encounter_id",
        "encounter__patient__patient_id",
        "encounter__patient__full_name",
        "encounter__patient__phone",
    )

    readonly_fields = (
        "invoice_id",
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = (
        "invoice",
        "clinical_order",
        "description",
        "quantity",
        "unit_price",
        "amount",
        "created_at",
    )

    list_filter = (
        "created_at",
    )

    search_fields = (
        "invoice__invoice_id",
        "clinical_order__order_id",
        "description",
    )

    readonly_fields = (
        "amount",
        "created_at",
    )

    ordering = ("-created_at",)

class PaymentAdminForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = (
            "invoice",
            "amount",
            "method",
            "reference",
            "received_by",
            "notes",
        )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    form = PaymentAdminForm

    list_display = (
        "payment_id",
        "invoice",
        "amount",
        "method",
        "received_by",
        "paid_at",
    )

    list_filter = (
        "method",
        "paid_at",
    )

    search_fields = (
        "payment_id",
        "invoice__invoice_id",
        "invoice__encounter__patient__patient_id",
        "invoice__encounter__patient__full_name",
        "reference",
    )

    readonly_fields = (
        "payment_id",
        "paid_at",
    )

    ordering = ("-paid_at",)

    def save_model(self, request, obj, form, change):
        if change:
            super().save_model(request, obj, form, change)
            return

        payment, invoice = record_payment(
            invoice_id=form.cleaned_data["invoice"].id,
            amount=form.cleaned_data["amount"],
            method=form.cleaned_data["method"],
            received_by=form.cleaned_data["received_by"],
            reference=form.cleaned_data["reference"],
            notes=form.cleaned_data["notes"],
        )

        obj.pk = payment.pk