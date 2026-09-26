from django.shortcuts import render


def clinic_home(request):
    return render(request, "clinic/home.html")