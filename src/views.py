from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from src.models import Customer, Project
from src.funks import validate_email, validate_password
from src.decorator.auth import customer_login_required, user_login_required

import jwt


def signup(request):
    if request.method == "GET":
        return render(request, "signup.html")
    else:
        email = request.POST.get("email")
        password = request.POST.get("password")

        success, message = validate_email(email)
        if not success:
            messages.error(request, message)
            return render(request, "signup.html")

        success, message = validate_password(password)
        if not success:
            messages.error(request, message)
            return render(request, "signup.html")

        Customer.objects.create(email=email, password=password)

        messages.success(request, "Account created successfully")
        return redirect("signin")


def signin(request):
    if request.method == "GET":
        return render(request, "signin.html")
    else:
        email = request.POST.get("email")
        password = request.POST.get("password")
        try:
            customer = Customer.objects.get(email=email)
            if customer.check_password(password):
                request.session["customer_id"] = customer.id
                return render(request, "dashboard.html")
            else:
                messages.error(request, "Invalid credentials")
                return render(request, "signin.html")
        except Customer.DoesNotExist:
            messages.error(request, "Invalid credentials")
            return render(request, "signin.html")


def logout(request):
    request.session.flush()
    return redirect("signin")


@customer_login_required
def dashboard(request):
    return render(request, "dashboard.html")


@customer_login_required
def create_project(request):
    if request.method == "GET":
        return render(request, "create_project.html")
    else:
        name = request.POST.get("name")
        if not name:
            messages.error(request, "Project name is required")
            return render(request, "create_project.html")
        description = request.POST.get("description")
        p_id = Project.objects.create(
            name=name, description=description, owner=request.customer
        ).id
        messages.success(request, "Project created successfully")
        return redirect("project_details", project_id=p_id)


@customer_login_required
def project_details(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
        return render(request, "project_details.html", {"project": project})
    except Project.DoesNotExist:
        messages.error(request, "Project not found")
        return render(request, "project_details.html")


def create_example_token(request, secret_key):
    return HttpResponse(
        jwt.encode(
            {
                "client_id": "123",
            },
            secret_key,
            algorithm="HS256",
        )
    )


@csrf_exempt
@user_login_required
def refresh_secret_key(request, project_id):
    try:
        Project.objects.get(id=project_id).refresh_secret_key()
        messages.success(request, "Secret key refreshed successfully")
        return HttpResponse("OK")
    except:
        return HttpResponse("Project not found", status=404)
