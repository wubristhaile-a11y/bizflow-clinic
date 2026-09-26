from django.contrib import admin

from .models import Department, DepartmentMembership


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "is_active",
        "updated_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "code",
        "description",
    )

    ordering = (
        "name",
    )


@admin.register(DepartmentMembership)
class DepartmentMembershipAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "organization",
        "department",
        "is_active",
        "created_at",
    )

    list_filter = (
        "organization",
        "department",
        "is_active",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "organization__name",
        "department__name",
    )

    ordering = (
        "organization",
        "department",
        "user",
    )