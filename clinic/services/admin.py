from django.contrib import admin

from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "department",
        "price",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "department",
        "is_active",
        "created_at",
    )

    search_fields = (
        "code",
        "name",
        "department__name",
        "department__code",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = ("department", "name")