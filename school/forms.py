from django import forms
from .models import (
    Student, Guardian, Enrollment, Attendance, Assessment,
    AssessmentResult, StudentInvoice, Payment, AcademicYear, Section,
)


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "first_name", "middle_name", "last_name", "sex",
            "date_of_birth", "phone", "email", "address", "admission_date",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "admission_date": forms.DateInput(attrs={"type": "date"}),
        }


class GuardianForm(forms.ModelForm):
    class Meta:
        model = Guardian
        fields = ["full_name", "relationship", "phone", "alternate_phone", "email", "address", "occupation"]


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ["academic_year", "section", "roll_number", "enrollment_date", "notes"]
        widgets = {"enrollment_date": forms.DateInput(attrs={"type": "date"})}


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ["status", "remarks"]


class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = [
            "academic_year", "term", "section", "subject",
            "name", "assessment_type", "max_mark", "date", "teacher",
        ]
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}


class AssessmentResultForm(forms.ModelForm):
    class Meta:
        model = AssessmentResult
        fields = ["mark", "remarks"]


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = StudentInvoice
        fields = ["academic_year", "due_date"]
        widgets = {"due_date": forms.DateInput(attrs={"type": "date"})}


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["amount", "method", "reference"]
