from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from src.forms import RegistrationForm
from src.models import Project, User, Domain
from src.funks import send_verify_email

import jwt
import threading
from datetime import datetime, timedelta


def index(request):
    if request.user.is_authenticated:
        return redirect("/admin")
    else:
        return redirect("/signup")


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
def refresh_secret_key(request, project):
    if request.method != "POST":
        return HttpResponse("NG", status=400)
    try:
        if request.user.is_superuser:
            Project.objects.get(name=project).refresh_secret_key()
        else:
            Project.objects.get(name=project, owner=request.user).refresh_secret_key()
        messages.success(request, "Secret key refreshed successfully")
        return HttpResponse("OK")
    except:
        return HttpResponse("NG", status=400)


def signup(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
                is_active=True,
                is_staff=True,
            )
            login(request, user)
            messages.success(request, "Signup successful.")
            messages.warning(request, "Check your email to authenticate your account before you can use the service.")
            cache.set(f"verify_email_{user.id}", True, 30)
            payload = {
                "user_id": request.user.id,
                "exp": datetime.utcnow() + timedelta(minutes=30),
            }
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
            threading.Thread(
                target=send_verify_email,
                args=(request.user, token),
            ).start()
            return redirect("/admin")
    else:
        form = RegistrationForm()

    return render(
        request,
        "admin/signup.html",
        {
            "form": form,
            "username": request.user.username,
            "site_header": "Websocket Service Admin"
        }
    )


def verify_email(request):
    token = request.GET.get("token")
    if token:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")
            user = User.objects.get(id=user_id)
            if user.verified:
                messages.warning(request, "Email already verified.")
                return redirect("/admin")
            user.verified = True
            # grant permission
            content_type = ContentType.objects.get_for_models(Project, Domain)
            permissions = (
                "add_project",
                "change_project",
                "delete_project",
                "add_domain",
                "change_domain",
                "delete_domain",
            )
            permission = Permission.objects.filter(
                codename__in=permissions,
                content_type__in=content_type.values(),
            )
            user.user_permissions.set(permission)
            user.save()
            messages.success(request, "Email verified successfully.")
            return redirect("/admin")
        except:
            raise Http404
        
    if request.user.is_authenticated:
        payload = {
            "user_id": request.user.id,
            "exp": datetime.utcnow() + timedelta(minutes=30),
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        threading.Thread(
            target=send_verify_email,
            args=(request.user, token),
        ).start()
        messages.success(request, f"Verification email sent to {request.user.email}")
        cache.set(f"verify_email_{request.user.id}", True, 60)
        next = request.GET.get('next')
        try:
            return redirect(next)
        except:
            return redirect('/admin')
    else:
        raise Http404
