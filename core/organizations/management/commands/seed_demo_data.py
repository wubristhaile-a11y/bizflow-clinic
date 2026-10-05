import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from core.organizations.models import (
    Organization,
    OrganizationMembership,
)
from clinic.departments.models import (
    Department,
    DepartmentMembership,
)


class Command(BaseCommand):
    help = "Initialize Wub Tech Solutions demo organizations, departments, and demo user."

    def handle(self, *args, **options):
        User = get_user_model()

        self.stdout.write("Initializing demo data...")

        # ============================================================
        # ORGANIZATIONS
        # ============================================================

        clinic, _ = Organization.objects.get_or_create(
            name="BizFlow Demo Clinic",
            defaults={
                "business_type": Organization.BusinessType.CLINIC,
                "city": "Gondar",
                "country": "Ethiopia",
                "currency": "ETB",
                "is_active": True,
            },
        )

        clinic.business_type = Organization.BusinessType.CLINIC
        clinic.is_active = True
        clinic.save()

        school, _ = Organization.objects.get_or_create(
            name="BizFlow Demo School",
            defaults={
                "business_type": Organization.BusinessType.SCHOOL,
                "city": "Gondar",
                "country": "Ethiopia",
                "currency": "ETB",
                "is_active": True,
            },
        )

        school.business_type = Organization.BusinessType.SCHOOL
        school.is_active = True
        school.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Organizations ready: {clinic.name}, {school.name}"
            )
        )

        # ============================================================
        # DEPARTMENTS
        # ============================================================

        departments = {
            "LAB": "Laboratory",
            "IMG": "Imaging",
            "END": "Endoscopy",
            "PHARM": "Pharmacy",
            "CONS": "Consultation",
            "RECEPTION": "Reception",
            "TRIAGE": "Triage",
            "BILLING": "Billing",
            "ADMIN": "Administration",
            "SCHOOL": "School Administration",
        }

        department_objects = {}

        for code, name in departments.items():
            department, _ = Department.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "is_active": True,
                },
            )

            department.name = name
            department.is_active = True
            department.save()

            department_objects[code] = department

        self.stdout.write(
            self.style.SUCCESS(
                f"Departments ready: {len(department_objects)}"
            )
        )

        # ============================================================
        # DEMO USER
        # ============================================================

        username = "WubristH"
        password = os.environ.get("DEMO_ADMIN_PASSWORD")

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": "wubristhaile@gmail.com",
                "is_active": True,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        if created:
            if not password:
                raise RuntimeError(
                    "DEMO_ADMIN_PASSWORD is required when creating "
                    "the WubristH production user."
                )

            user.set_password(password)
            user.save()

            self.stdout.write(
                self.style.SUCCESS(
                    "Created production demo user: WubristH"
                )
            )

        else:
            changed = False

            if not user.is_active:
                user.is_active = True
                changed = True

            if not user.is_staff:
                user.is_staff = True
                changed = True

            if not user.is_superuser:
                user.is_superuser = True
                changed = True

            if changed:
                user.save()

            self.stdout.write(
                self.style.SUCCESS(
                    "Existing demo user verified: WubristH"
                )
            )

        # ============================================================
        # ORGANIZATION MEMBERSHIPS
        # ============================================================

        OrganizationMembership.objects.update_or_create(
            user=user,
            organization=clinic,
            defaults={
                "role": OrganizationMembership.Role.OWNER,
                "is_active": True,
            },
        )

        OrganizationMembership.objects.update_or_create(
            user=user,
            organization=school,
            defaults={
                "role": OrganizationMembership.Role.OWNER,
                "is_active": True,
            },
        )

        # ============================================================
        # CLINIC DEPARTMENT ACCESS
        # ============================================================

        clinic_departments = [
            "LAB",
            "IMG",
            "END",
            "PHARM",
            "CONS",
            "RECEPTION",
            "TRIAGE",
            "BILLING",
            "ADMIN",
        ]

        for code in clinic_departments:
            DepartmentMembership.objects.update_or_create(
                user=user,
                organization=clinic,
                department=department_objects[code],
                defaults={
                    "is_active": True,
                },
            )

        # ============================================================
        # SCHOOL DEPARTMENT ACCESS
        # ============================================================

        DepartmentMembership.objects.update_or_create(
            user=user,
            organization=school,
            department=department_objects["SCHOOL"],
            defaults={
                "is_active": True,
            },
        )

        self.stdout.write(
            self.style.SUCCESS(
                "WubristH department access initialized."
            )
        )

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "Demo database initialization completed successfully."
            )
        )