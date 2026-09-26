from django.conf import settings
from django.db import models


class Organization(models.Model):
    """
    A business/company using BizFlow.
    """

    class BusinessType(models.TextChoices):
        RETAIL = "RETAIL", "Retail"
        WHOLESALE = "WHOLESALE", "Wholesale"
        MANUFACTURING = "MANUFACTURING", "Manufacturing"
        SERVICE = "SERVICE", "Service"
        RESTAURANT = "RESTAURANT", "Restaurant"
        HOTEL = "HOTEL", "Hotel"
        SCHOOL = "SCHOOL", "School"
        CLINIC = "CLINIC", "Clinic"
        DELIVERY = "DELIVERY", "Delivery"
        OTHER = "OTHER", "Other"

    name = models.CharField(max_length=200)

    business_type = models.CharField(
        max_length=30,
        choices=BusinessType.choices,
        default=BusinessType.OTHER,
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
    )

    email = models.EmailField(
        blank=True,
    )

    address = models.TextField(
        blank=True,
    )

    city = models.CharField(
        max_length=100,
        blank=True,
    )

    country = models.CharField(
        max_length=100,
        default="Ethiopia",
    )

    currency = models.CharField(
        max_length=3,
        default="ETB",
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return self.name


class OrganizationMembership(models.Model):
    """
    Connects a User to an Organization.

    A user can belong to multiple organizations.
    """

    class Role(models.TextChoices):
        OWNER = "OWNER", "Owner"
        ADMIN = "ADMIN", "Administrator"
        MANAGER = "MANAGER", "Manager"
        STAFF = "STAFF", "Staff"
        STOREKEEPER = "STOREKEEPER", "Storekeeper"
        ACCOUNTANT = "ACCOUNTANT", "Accountant"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organization_memberships",
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="memberships",
    )

    role = models.CharField(
        max_length=30,
        choices=Role.choices,
        default=Role.STAFF,
    )

    is_active = models.BooleanField(
        default=True,
    )

    joined_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "organization"],
                name="unique_user_organization",
            ),
        ]

    def __str__(self):
        return f"{self.user} → {self.organization} ({self.role})"
