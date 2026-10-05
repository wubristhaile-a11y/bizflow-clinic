from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils import timezone


class School(models.Model):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.PROTECT,
        related_name="schools",
    )
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=30, unique=True)
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    principal_name = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class AcademicYear(models.Model):
    school = models.ForeignKey(School, on_delete=models.PROTECT, related_name="academic_years")
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ["-start_date"]
        constraints = [
            models.UniqueConstraint(fields=["school", "name"], name="unique_school_academic_year")
        ]

    def __str__(self):
        return self.name


class Term(models.Model):
    school = models.ForeignKey(School, on_delete=models.PROTECT, related_name="terms")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="terms")
    name = models.CharField(max_length=50)
    number = models.PositiveSmallIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ["academic_year", "number"]
        constraints = [
            models.UniqueConstraint(
                fields=["academic_year", "number"],
                name="unique_academic_year_term",
            )
        ]

    def __str__(self):
        return f"{self.academic_year.name} - {self.name}"


class GradeLevel(models.Model):
    school = models.ForeignKey(School, on_delete=models.PROTECT, related_name="grade_levels")
    name = models.CharField(max_length=80)
    code = models.CharField(max_length=30)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]
        constraints = [
            models.UniqueConstraint(fields=["school", "code"], name="unique_school_grade_code")
        ]

    def __str__(self):
        return self.name


class Section(models.Model):
    school = models.ForeignKey(School, on_delete=models.PROTECT, related_name="sections")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="sections")
    grade = models.ForeignKey(GradeLevel, on_delete=models.PROTECT, related_name="sections")
    name = models.CharField(max_length=50)
    room = models.CharField(max_length=50, blank=True)
    class_teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="school_class_sections",
    )
    capacity = models.PositiveIntegerField(default=40)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["grade__order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["academic_year", "grade", "name"],
                name="unique_year_grade_section",
            )
        ]

    def __str__(self):
        return f"{self.grade.name} - {self.name}"


class Guardian(models.Model):
    full_name = models.CharField(max_length=150)
    relationship = models.CharField(max_length=80, blank=True)
    phone = models.CharField(max_length=30)
    alternate_phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    occupation = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return self.full_name


class Student(models.Model):
    class Sex(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"

    student_id = models.CharField(max_length=30, unique=True, editable=False)
    school = models.ForeignKey(School, on_delete=models.PROTECT, related_name="students")
    first_name = models.CharField(max_length=80)
    middle_name = models.CharField(max_length=80, blank=True)
    last_name = models.CharField(max_length=80)
    sex = models.CharField(max_length=1, choices=Sex.choices)
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    admission_date = models.DateField(default=timezone.now)
    guardians = models.ManyToManyField(Guardian, blank=True, related_name="students")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    @property
    def full_name(self):
        return " ".join(p for p in [self.first_name, self.middle_name, self.last_name] if p)

    def save(self, *args, **kwargs):
        if not self.student_id:
            last = Student.objects.order_by("-id").first()
            next_number = (last.id + 1) if last else 1
            self.student_id = f"BF-S-{next_number:06d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student_id} - {self.full_name}"


class Enrollment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"
        TRANSFERRED = "TRANSFERRED", "Transferred"
        WITHDRAWN = "WITHDRAWN", "Withdrawn"

    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="enrollments")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="enrollments")
    section = models.ForeignKey(Section, on_delete=models.PROTECT, related_name="enrollments")
    roll_number = models.PositiveIntegerField(null=True, blank=True)
    enrollment_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["section__grade__order", "section__name", "roll_number", "student__last_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "academic_year"],
                name="unique_student_year_enrollment",
            )
        ]

    def __str__(self):
        return f"{self.student.full_name} - {self.section}"


class Subject(models.Model):
    school = models.ForeignKey(School, on_delete=models.PROTECT, related_name="subjects")
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=30)
    max_mark = models.DecimalField(max_digits=6, decimal_places=2, default=100)
    pass_mark = models.DecimalField(max_digits=6, decimal_places=2, default=50)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["school", "code"], name="unique_school_subject_code")
        ]

    def __str__(self):
        return self.name


class Teacher(models.Model):
    school = models.ForeignKey(School, on_delete=models.PROTECT, related_name="teachers")
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="school_teacher_profile",
    )
    employee_id = models.CharField(max_length=40, unique=True)
    qualification = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name() or self.user.username}"


class TeacherSubject(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="subjects")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="teachers")
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="teacher_subjects")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["teacher", "subject", "section"],
                name="unique_teacher_subject_section",
            )
        ]


class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = "PRESENT", "Present"
        ABSENT = "ABSENT", "Absent"
        LATE = "LATE", "Late"
        EXCUSED = "EXCUSED", "Excused"

    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="attendance")
    date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices)
    remarks = models.CharField(max_length=255, blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="school_attendance_records",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "enrollment__student__last_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["enrollment", "date"],
                name="unique_enrollment_attendance_date",
            )
        ]


class Assessment(models.Model):
    class Type(models.TextChoices):
        QUIZ = "QUIZ", "Quiz"
        ASSIGNMENT = "ASSIGNMENT", "Assignment"
        MIDTERM = "MIDTERM", "Midterm"
        FINAL = "FINAL", "Final"
        PROJECT = "PROJECT", "Project"

    school = models.ForeignKey(School, on_delete=models.PROTECT, related_name="assessments")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="assessments")
    term = models.ForeignKey(Term, on_delete=models.PROTECT, related_name="assessments")
    section = models.ForeignKey(Section, on_delete=models.PROTECT, related_name="assessments")
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name="assessments")
    name = models.CharField(max_length=120)
    assessment_type = models.CharField(max_length=20, choices=Type.choices)
    max_mark = models.DecimalField(max_digits=6, decimal_places=2, default=100)
    date = models.DateField(default=timezone.now)
    teacher = models.ForeignKey(Teacher, on_delete=models.PROTECT, related_name="assessments")

    class Meta:
        ordering = ["-date", "name"]


class AssessmentResult(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="results")
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="assessment_results")
    mark = models.DecimalField(max_digits=7, decimal_places=2)
    remarks = models.CharField(max_length=255, blank=True)
    recorded_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["assessment", "enrollment"],
                name="unique_assessment_enrollment_result",
            )
        ]

    @property
    def percentage(self):
        if not self.assessment.max_mark:
            return Decimal("0")
        return (self.mark / self.assessment.max_mark) * Decimal("100")


class FeeType(models.Model):
    school = models.ForeignKey(School, on_delete=models.PROTECT, related_name="fee_types")
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["school", "name"], name="unique_school_fee_name")
        ]

    def __str__(self):
        return self.name


class StudentInvoice(models.Model):
    class Status(models.TextChoices):
        UNPAID = "UNPAID", "Unpaid"
        PARTIALLY_PAID = "PARTIALLY_PAID", "Partially paid"
        PAID = "PAID", "Paid"
        CANCELLED = "CANCELLED", "Cancelled"

    invoice_id = models.CharField(max_length=30, unique=True, editable=False)
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="school_invoices")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="invoices")
    issued_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UNPAID)

    @property
    def total(self):
        return sum((item.amount for item in self.items.all()), Decimal("0"))

    @property
    def paid(self):
        return sum((p.amount for p in self.payments.filter(status=Payment.Status.COMPLETED)), Decimal("0"))

    @property
    def balance(self):
        return max(self.total - self.paid, Decimal("0"))

    def save(self, *args, **kwargs):
        if not self.invoice_id:
            last = StudentInvoice.objects.order_by("-id").first()
            next_number = (last.id + 1) if last else 1
            self.invoice_id = f"SF-{next_number:06d}"
        super().save(*args, **kwargs)


class StudentInvoiceItem(models.Model):
    invoice = models.ForeignKey(StudentInvoice, on_delete=models.CASCADE, related_name="items")
    fee_type = models.ForeignKey(FeeType, on_delete=models.PROTECT, related_name="invoice_items")
    description = models.CharField(max_length=255, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_amount = models.DecimalField(max_digits=12, decimal_places=2)

    @property
    def amount(self):
        return self.quantity * self.unit_amount


class Payment(models.Model):
    class Method(models.TextChoices):
        CASH = "CASH", "Cash"
        BANK = "BANK", "Bank transfer"
        CARD = "CARD", "Card"
        MOBILE = "MOBILE", "Mobile money"
        OTHER = "OTHER", "Other"

    class Status(models.TextChoices):
        COMPLETED = "COMPLETED", "Completed"
        VOID = "VOID", "Void"

    invoice = models.ForeignKey(StudentInvoice, on_delete=models.PROTECT, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=20, choices=Method.choices, default=Method.CASH)
    reference = models.CharField(max_length=100, blank=True)
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="school_payments_received",
    )
    paid_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.COMPLETED)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        invoice = self.invoice
        balance = invoice.balance
        if balance <= 0 and invoice.total > 0:
            invoice.status = StudentInvoice.Status.PAID
        elif invoice.paid > 0:
            invoice.status = StudentInvoice.Status.PARTIALLY_PAID
        else:
            invoice.status = StudentInvoice.Status.UNPAID
        invoice.save(update_fields=["status"])
class TransferHistory(models.Model):
    """
    Stores academic history brought from another school.
    Used for students transferring into the school.
    """

    student = models.ForeignKey(
        "Student",
        on_delete=models.CASCADE,
        related_name="transfer_histories",
    )

    previous_school_name = models.CharField(max_length=255)
    previous_school_address = models.CharField(
        max_length=500,
        blank=True,
    )
    previous_school_student_id = models.CharField(
        max_length=100,
        blank=True,
    )

    admission_grade = models.CharField(
        max_length=100,
        blank=True,
    )

    transfer_date = models.DateField(
        null=True,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.student} - "
            f"{self.previous_school_name}"
        )


class TransferAcademicRecord(models.Model):
    """
    One academic record from a student's previous school.

    Example:
    Grade 5 / 2024-2025 / Mathematics / 78 / 100
    """

    transfer_history = models.ForeignKey(
        TransferHistory,
        on_delete=models.CASCADE,
        related_name="academic_records",
    )

    academic_year = models.CharField(
        max_length=50,
    )

    grade_name = models.CharField(
        max_length=100,
    )

    term_name = models.CharField(
        max_length=100,
        blank=True,
    )

    subject_name = models.CharField(
        max_length=150,
    )

    mark = models.DecimalField(
        max_digits=7,
        decimal_places=2,
    )

    maximum_mark = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=100,
    )

    letter_grade = models.CharField(
        max_length=20,
        blank=True,
    )

    remarks = models.CharField(
        max_length=500,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "academic_year",
            "grade_name",
            "term_name",
            "subject_name",
        ]

    @property
    def percentage(self):
        if not self.maximum_mark:
            return 0

        return round(
            (self.mark / self.maximum_mark) * 100,
            2,
        )

    def __str__(self):
        return (
            f"{self.student_name} - "
            f"{self.grade_name} - "
            f"{self.subject_name}"
        )

    @property
    def student_name(self):
        return self.transfer_history.student