from datetime import date
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from core.organizations.models import Organization
from clinic.departments.models import Department, DepartmentMembership
from school.models import (
    School, AcademicYear, Term, GradeLevel, Section, Subject, Teacher,
    FeeType,
)

class Command(BaseCommand):
    help = "Create an idempotent BizFlow School demo organization/workspace."

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        username = "schooladmin"
        password = "SchoolDemo123!"
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"first_name": "School", "last_name": "Administrator", "is_active": True},
        )
        if created:
            user.set_password(password)
            user.save()

        org, _ = Organization.objects.get_or_create(
            name="BizFlow Demo School",
            defaults={
                "business_type": "SCHOOL",
                "city": "Gondar",
                "country": "Ethiopia",
                "currency": "ETB",
                "is_active": True,
            },
        )

        department, _ = Department.objects.get_or_create(
            code="SCHOOL",
            defaults={"name": "School Administration", "is_active": True},
        )
        DepartmentMembership.objects.get_or_create(
            user=user, organization=org, department=department,
            defaults={"is_active": True},
        )

        school, _ = School.objects.get_or_create(
            code="BFS-DEMO",
            defaults={
                "organization": org,
                "name": "BizFlow Demo School",
                "address": "Gondar, Ethiopia",
                "phone": "+251 900 000 000",
                "principal_name": "Demo Principal",
                "is_active": True,
            },
        )

        year, _ = AcademicYear.objects.get_or_create(
            school=school,
            name="2026/2027",
            defaults={
                "start_date": date(2026, 9, 1),
                "end_date": date(2027, 7, 31),
                "is_current": True,
            },
        )
        Term.objects.get_or_create(
            school=school, academic_year=year, number=1,
            defaults={"name": "Term 1", "start_date": date(2026, 9, 1), "end_date": date(2026, 12, 31), "is_current": True},
        )
        Term.objects.get_or_create(
            school=school, academic_year=year, number=2,
            defaults={"name": "Term 2", "start_date": date(2027, 1, 1), "end_date": date(2027, 3, 31), "is_current": False},
        )
        Term.objects.get_or_create(
            school=school, academic_year=year, number=3,
            defaults={"name": "Term 3", "start_date": date(2027, 4, 1), "end_date": date(2027, 7, 31), "is_current": False},
        )

        grades = []
        for order, (name, code) in enumerate([
            ("Grade 1", "G1"), ("Grade 2", "G2"), ("Grade 3", "G3"),
            ("Grade 4", "G4"), ("Grade 5", "G5"), ("Grade 6", "G6"),
            ("Grade 7", "G7"), ("Grade 8", "G8"),
        ], 1):
            grade, _ = GradeLevel.objects.get_or_create(
                school=school, code=code,
                defaults={"name": name, "order": order, "is_active": True},
            )
            grades.append(grade)

        for grade in grades[:4]:
            for section_name in ["A", "B"]:
                Section.objects.get_or_create(
                    school=school, academic_year=year, grade=grade, name=section_name,
                    defaults={"capacity": 40, "is_active": True},
                )

        for code, name in [
            ("ENG", "English"), ("MATH", "Mathematics"), ("SCI", "Science"),
            ("AMH", "Amharic"), ("SOC", "Social Studies"), ("ICT", "ICT"),
        ]:
            Subject.objects.get_or_create(
                school=school, code=code,
                defaults={"name": name, "max_mark": 100, "pass_mark": 50, "is_active": True},
            )

        for name, amount in [
            ("Tuition", 2500),
            ("Registration", 500),
            ("Library", 150),
            ("Laboratory", 250),
        ]:
            FeeType.objects.get_or_create(
                school=school, name=name,
                defaults={"amount": amount, "is_active": True},
            )

        self.stdout.write(self.style.SUCCESS("School demo created/verified."))
        self.stdout.write(f"Login: {username}")
        if created:
            self.stdout.write(f"Password: {password}")
        else:
            self.stdout.write("Existing user password was NOT changed.")
