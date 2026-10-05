from django.shortcuts import render


def home(request):
    """
    Public Wub Tech Solutions landing page.

    This is the company/platform home, not an organization dashboard.
    Individual products such as Clinic and School have their own dashboards.
    """
    solutions = [
        {
            "name": "Clinic Management",
            "category": "Healthcare",
            "description": (
                "Connected patient, clinical, laboratory, pharmacy, "
                "and billing workflows."
            ),
            "icon": "bi-heart-pulse",
            "url": "/clinic/",
            "status": "Live Demo",
            "status_class": "success",
            "background_class": "clinic",
        },
        {
            "name": "School Management",
            "category": "Education",
            "description": (
                "Student, academic, attendance, assessment, transcript, "
                "and school finance management."
            ),
            "icon": "bi-mortarboard",
            "url": "/school/",
            "status": "Live Demo",
            "status_class": "success",
            "background_class": "school",
        },
        {
            "name": "Delivery Management",
            "category": "Logistics",
            "description": (
                "Delivery operations, riders, orders, tracking, "
                "and payment workflows."
            ),
            "icon": "bi-truck",
            "url": "#",
            "status": "Coming Soon",
            "status_class": "secondary",
            "background_class": "delivery",
        },
        {
            "name": "Business Operations",
            "category": "Business",
            "description": (
                "Flexible tools for organizations to manage people, "
                "operations, records, and finances."
            ),
            "icon": "bi-building",
            "url": "#",
            "status": "Coming Soon",
            "status_class": "secondary",
            "background_class": "business",
        },
    ]

    return render(
        request,
        "home.html",
        {
            "solutions": solutions,
        },
    )