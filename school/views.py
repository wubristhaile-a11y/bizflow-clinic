from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, redirect, render

from core.department_access import department_required
from .forms import (
    StudentForm, GuardianForm, EnrollmentForm, AttendanceForm,
    AssessmentForm, AssessmentResultForm, InvoiceForm, PaymentForm,
)
from .models import (
    School, Student, Guardian, Enrollment, Attendance,
    Assessment, AssessmentResult, StudentInvoice, StudentInvoiceItem,
    FeeType, Payment,
)


def get_school(request):
    return (
        School.objects
        .filter(
            organization__department_memberships__user=request.user,
            organization__department_memberships__department__code="SCHOOL",
            organization__department_memberships__is_active=True,
            organization__is_active=True,
            is_active=True,
        )
        .distinct()
        .first()
    )


@login_required
@department_required("SCHOOL")
def dashboard(request):
    school = get_school(request)
    if not school:
        return render(request, "school/no_school.html")

    current_year = school.academic_years.filter(is_current=True).first()
    active_students = Student.objects.filter(school=school, is_active=True).count()
    active_enrollments = Enrollment.objects.filter(
        academic_year=current_year,
        status=Enrollment.Status.ACTIVE,
    ).count() if current_year else 0
    sections = school.sections.filter(is_active=True).count()
    unpaid = StudentInvoice.objects.filter(
        student__school=school,
        status__in=[StudentInvoice.Status.UNPAID, StudentInvoice.Status.PARTIALLY_PAID],
    ).count()

    return render(request, "school/dashboard.html", {
        "school": school,
        "current_year": current_year,
        "active_students": active_students,
        "active_enrollments": active_enrollments,
        "sections": sections,
        "unpaid": unpaid,
    })


@login_required
@department_required("SCHOOL")
def student_list(request):
    school = get_school(request)
    q = request.GET.get("q", "").strip()
    students = Student.objects.filter(school=school, is_active=True)
    if q:
        students = students.filter(
            Q(student_id__icontains=q)
            | Q(first_name__icontains=q)
            | Q(middle_name__icontains=q)
            | Q(last_name__icontains=q)
            | Q(phone__icontains=q)
        )
    return render(request, "school/student_list.html", {"school": school, "students": students, "q": q})


@login_required
@department_required("SCHOOL")
def student_create(request):
    school = get_school(request)
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.school = school
            student.save()
            messages.success(request, f"Student {student.student_id} registered successfully.")
            return redirect("school:student_detail", student_id=student.id)
    else:
        form = StudentForm(initial={"admission_date": date.today()})
    return render(request, "school/student_form.html", {"form": form, "school": school})


@login_required
@department_required("SCHOOL")
def student_detail(request, student_id):
    school = get_school(request)
    student = get_object_or_404(
        Student.objects.prefetch_related("guardians", "enrollments__section__grade"),
        id=student_id,
        school=school,
    )
    guardians = student.guardians.all()
    enrollments = student.enrollments.select_related("academic_year", "section__grade").all()
    invoices = student.school_invoices.prefetch_related("items", "payments").order_by("-issued_at")
    return render(request, "school/student_detail.html", {
        "school": school, "student": student, "guardians": guardians,
        "enrollments": enrollments, "invoices": invoices,
    })


@login_required
@department_required("SCHOOL")
def guardian_add(request, student_id):
    school = get_school(request)
    student = get_object_or_404(Student, id=student_id, school=school)
    if request.method == "POST":
        form = GuardianForm(request.POST)
        if form.is_valid():
            guardian = form.save()
            student.guardians.add(guardian)
            messages.success(request, "Guardian added.")
            return redirect("school:student_detail", student.id)
    else:
        form = GuardianForm()
    return render(request, "school/guardian_form.html", {"form": form, "student": student})


@login_required
@department_required("SCHOOL")
def enrollment_create(request, student_id):
    school = get_school(request)
    student = get_object_or_404(Student, id=student_id, school=school)
    if request.method == "POST":
        form = EnrollmentForm(request.POST)
        form.fields["academic_year"].queryset = school.academic_years.all()
        form.fields["section"].queryset = school.sections.filter(is_active=True)
        if form.is_valid():
            enrollment = form.save(commit=False)
            if enrollment.section.academic_year_id != enrollment.academic_year_id:
                form.add_error("section", "Section does not belong to the selected academic year.")
            else:
                enrollment.student = student
                enrollment.save()
                messages.success(request, "Student enrolled successfully.")
                return redirect("school:student_detail", student.id)
    else:
        form = EnrollmentForm()
        form.fields["academic_year"].queryset = school.academic_years.all()
        form.fields["section"].queryset = school.sections.filter(is_active=True)
    return render(request, "school/enrollment_form.html", {"form": form, "student": student})


@login_required
@department_required("SCHOOL")
def attendance(request):
    school = get_school(request)
    year = school.academic_years.filter(is_current=True).first()
    sections = school.sections.filter(academic_year=year, is_active=True) if year else []
    selected_section = request.GET.get("section")
    section = get_object_or_404(school.sections, id=selected_section) if selected_section else None
    if section and year and section.academic_year_id != year.id:
        section = None

    enrollments = []
    if section:
        enrollments = list(
            Enrollment.objects.filter(
                section=section,
                academic_year=year,
                status=Enrollment.Status.ACTIVE,
            ).select_related("student").order_by("roll_number", "student__last_name")
        )

    if request.method == "POST" and section:
        attendance_date = request.POST.get("attendance_date") or str(date.today())
        for enrollment in enrollments:
            status = request.POST.get(f"status_{enrollment.id}", Attendance.Status.ABSENT)
            Attendance.objects.update_or_create(
                enrollment=enrollment,
                date=attendance_date,
                defaults={"status": status, "recorded_by": request.user},
            )
        messages.success(request, "Attendance saved.")
        return redirect(f"/school/attendance/?section={section.id}")

    return render(request, "school/attendance.html", {
        "school": school, "year": year, "sections": sections,
        "section": section, "enrollments": enrollments, "today": date.today(),
    })


@login_required
@department_required("SCHOOL")
def assessment_list(request):
    school = get_school(request)
    assessments = (
        Assessment.objects.filter(school=school)
        .select_related("term", "section__grade", "subject", "teacher__user")
        .order_by("-date")
    )
    return render(request, "school/assessment_list.html", {"school": school, "assessments": assessments})


@login_required
@department_required("SCHOOL")
def assessment_create(request):
    school = get_school(request)
    if request.method == "POST":
        form = AssessmentForm(request.POST)
        form.fields["academic_year"].queryset = school.academic_years.all()
        form.fields["term"].queryset = school.terms.all()
        form.fields["section"].queryset = school.sections.filter(is_active=True)
        form.fields["subject"].queryset = school.subjects.filter(is_active=True)
        form.fields["teacher"].queryset = school.teachers.filter(is_active=True)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.school = school
            assessment.save()
            messages.success(request, "Assessment created.")
            return redirect("school:assessment_detail", assessment.id)
    else:
        form = AssessmentForm()
        form.fields["academic_year"].queryset = school.academic_years.all()
        form.fields["term"].queryset = school.terms.all()
        form.fields["section"].queryset = school.sections.filter(is_active=True)
        form.fields["subject"].queryset = school.subjects.filter(is_active=True)
        form.fields["teacher"].queryset = school.teachers.filter(is_active=True)
    return render(request, "school/assessment_form.html", {"form": form, "school": school})


@login_required
@department_required("SCHOOL")
def assessment_detail(request, assessment_id):
    school = get_school(request)
    assessment = get_object_or_404(
        Assessment.objects.select_related("section__grade", "subject", "term"),
        id=assessment_id, school=school,
    )
    enrollments = Enrollment.objects.filter(
        section=assessment.section,
        academic_year=assessment.academic_year,
        status=Enrollment.Status.ACTIVE,
    ).select_related("student").order_by("roll_number", "student__last_name")

    if request.method == "POST":
        with transaction.atomic():
            for enrollment in enrollments:
                mark = request.POST.get(f"mark_{enrollment.id}", "").strip()
                remarks = request.POST.get(f"remarks_{enrollment.id}", "").strip()
                if mark != "":
                    AssessmentResult.objects.update_or_create(
                        assessment=assessment,
                        enrollment=enrollment,
                        defaults={"mark": mark, "remarks": remarks},
                    )
        messages.success(request, "Gradebook saved.")
        return redirect("school:assessment_detail", assessment.id)

    results = {r.enrollment_id: r for r in assessment.results.all()}
    return render(request, "school/assessment_detail.html", {
        "school": school, "assessment": assessment,
        "enrollments": enrollments, "results": results,
    })


@login_required
@department_required("SCHOOL")
def invoice_list(request):
    school = get_school(request)
    invoices = (
        StudentInvoice.objects.filter(student__school=school)
        .select_related("student", "academic_year")
        .prefetch_related("items")
        .order_by("-issued_at")
    )
    return render(request, "school/invoice_list.html", {"school": school, "invoices": invoices})


@login_required
@department_required("SCHOOL")
def invoice_create(request, student_id):
    school = get_school(request)
    student = get_object_or_404(Student, id=student_id, school=school)
    fees = FeeType.objects.filter(school=school, is_active=True)
    if request.method == "POST":
        form = InvoiceForm(request.POST)
        form.fields["academic_year"].queryset = school.academic_years.all()
        fee_id = request.POST.get("fee_type")
        fee = get_object_or_404(fees, id=fee_id)
        quantity = max(int(request.POST.get("quantity", "1") or 1), 1)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.student = student
            invoice.save()
            StudentInvoiceItem.objects.create(
                invoice=invoice,
                fee_type=fee,
                description=fee.description or fee.name,
                quantity=quantity,
                unit_amount=fee.amount,
            )
            messages.success(request, f"Invoice {invoice.invoice_id} created.")
            return redirect("school:invoice_detail", invoice.id)
    else:
        form = InvoiceForm()
        form.fields["academic_year"].queryset = school.academic_years.all()
    return render(request, "school/invoice_form.html", {
        "form": form, "student": student, "fees": fees, "school": school,
    })


@login_required
@department_required("SCHOOL")
def invoice_detail(request, invoice_id):
    school = get_school(request)
    invoice = get_object_or_404(
        StudentInvoice.objects.select_related("student", "academic_year")
        .prefetch_related("items", "payments"),
        id=invoice_id, student__school=school,
    )
    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.invoice = invoice
            if payment.amount <= 0 or payment.amount > invoice.balance:
                form.add_error("amount", f"Enter an amount up to the remaining balance ({invoice.balance}).")
            else:
                payment.received_by = request.user
                payment.save()
                messages.success(request, "Payment recorded.")
                return redirect("school:invoice_detail", invoice.id)
    else:
        form = PaymentForm(initial={"amount": invoice.balance})
    return render(request, "school/invoice_detail.html", {
        "school": school, "invoice": invoice, "form": form,
    })


@login_required
@department_required("SCHOOL")
def report_card(request, student_id):
    school = get_school(request)
    student = get_object_or_404(Student, id=student_id, school=school)
    year = school.academic_years.filter(is_current=True).first()
    enrollment = student.enrollments.filter(academic_year=year, status=Enrollment.Status.ACTIVE).select_related("section__grade").first() if year else None
    results = []
    if enrollment:
        results = (
            AssessmentResult.objects
            .filter(enrollment=enrollment)
            .select_related("assessment__subject", "assessment__term")
            .order_by("assessment__term__number", "assessment__subject__name", "assessment__date")
        )
    return render(request, "school/report_card.html", {
        "school": school, "student": student, "year": year,
        "enrollment": enrollment, "results": results,
    })
