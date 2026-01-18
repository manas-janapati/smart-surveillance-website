from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from detections.models import Survey

def login_view(request):
    if request.user.is_authenticated:
        return redirect("worker_home")

    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST["username"],
            password=request.POST["password"],
        )
        if user:
            login(request, user)
            return redirect("worker_home")

    return render(request, "workers/login.html")



@login_required
def home(request):
    surveys = Survey.objects.order_by("-uploaded_at")
    return render(
        request,
        "workers/home.html",
        {"surveys": surveys}
    )



@login_required
def survey_page(request, survey_id):
    return render(
        request,
        "workers/survey.html",
        {"survey_id": survey_id}
    )


@login_required
def profile(request):
    return render(request, "workers/profile.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("worker_login")
