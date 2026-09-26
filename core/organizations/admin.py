from django.contrib import admin

from .models import Organization, OrganizationMembership


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "business_type",
        "city",
        "currency",
        "is_active",
        "created_at",
    )

    list_filter = (
        "business_type",
        "is_active",
        "currency",
    )

    search_fields = (
        "name",
        "phone",
        "email",
        "city",
    )


@admin.register(OrganizationMembership)
class OrganizationMembershipAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "organization",
        "role",
        "is_active",
        "joined_at",
    )

    list_filter = (
        "role",
        "is_active",
    )

    search_fields = (
        "user__username",
        "organization__name",
    )