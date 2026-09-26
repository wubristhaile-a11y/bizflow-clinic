from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            "BizFlow Information",
            {
                "fields": (
                    "phone",
                ),
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "BizFlow Information",
            {
                "fields": (
                    "phone",
                ),
            },
        ),
    )