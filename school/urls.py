from django.urls import path
from . import views

app_name = "school"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("students/", views.student_list, name="student_list"),
    path("students/new/", views.student_create, name="student_create"),
    path("students/<int:student_id>/", views.student_detail, name="student_detail"),
    path("students/<int:student_id>/guardian/", views.guardian_add, name="guardian_add"),
    path("students/<int:student_id>/enroll/", views.enrollment_create, name="enrollment_create"),
    path("students/<int:student_id>/invoice/new/", views.invoice_create, name="invoice_create"),
    path("students/<int:student_id>/report-card/", views.report_card, name="report_card"),
    path("attendance/", views.attendance, name="attendance"),
    path("assessments/", views.assessment_list, name="assessment_list"),
    path("assessments/new/", views.assessment_create, name="assessment_create"),
    path("assessments/<int:assessment_id>/", views.assessment_detail, name="assessment_detail"),
    path("invoices/", views.invoice_list, name="invoice_list"),
    path("invoices/<int:invoice_id>/", views.invoice_detail, name="invoice_detail"),
]
