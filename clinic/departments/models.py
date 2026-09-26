from django.conf import settings
from django.db import models

from core.organizations.models import Organization


class Department(models.Model):
    name = models.CharField(max_length=100)

    code = models.CharField(
        max_length=20,
        unique=True,
    )

    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class DepartmentMembership(models.Model):
    """
    Connects a staff user to a clinic department.

    A user can belong to a department within an organization,
    and the same user can potentially belong to another department
    in another organization.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="department_memberships",
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name="department_memberships",
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="memberships",
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "organization", "department"],
                name="unique_user_org_department",
            )
        ]

    def __str__(self):
        return (
            f"{self.user.username} → "
            f"{self.organization.name} → "
            f"{self.department.name}"
        )