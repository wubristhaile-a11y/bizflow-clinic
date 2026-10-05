from django.contrib import admin
from .models import (
    School, AcademicYear, Term, GradeLevel, Section, Guardian, Student,
    Enrollment, Subject, Teacher, TeacherSubject, Attendance, Assessment,
    AssessmentResult, FeeType, StudentInvoice, StudentInvoiceItem, Payment,
)

admin.site.register([
    School, AcademicYear, Term, GradeLevel, Section, Guardian, Student,
    Enrollment, Subject, Teacher, TeacherSubject, Attendance, Assessment,
    AssessmentResult, FeeType, StudentInvoice, StudentInvoiceItem, Payment,
])
