from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.views.generic.edit import FormView
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordContextMixin
from django.contrib.auth.forms import SetPasswordForm

from src.forms import RegistrationForm, PasswordResetForm
from src.models import Project, User, Domain
from src.funks import (
    send_verify_email,
    send_password_reset_email,
    check_token_used,
    set_token_used,
)

import jwt
import threading
from datetime import datetime, timedelta
import logging
import secrets


def index(request):
    return redirect("dashboard:index")


def refresh_secret_key(request, project):
    if request.method != "POST":
        return HttpResponse("NG", status=400)
    try:
        if request.user.is_superuser:
            Project.objects.get(name=project).refresh_secret_key()
        else:
            Project.objects.get(name=project, owner=request.user).refresh_secret_key()
        messages.success(
            request,
            "Successfully refreshed the secret key, but it only applies to new connections.",
        )
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
            messages.warning(
                request,
                "Check your email to authenticate your account before you can use the service.",
            )
            verify_code = secrets.token_hex(48)
            cache.set(f"verify_email_code_{user.id}", verify_code, 1800)
            cache.set(f"verify_email_notice_{user.id}", True, 30)
            cache.set(verify_code, request.user.id, 1800)
            threading.Thread(
                target=send_verify_email,
                args=(request, request.user, verify_code),
            ).start()
            return redirect("dashboard:index")
    else:
        form = RegistrationForm()

    return render(
        request,
        "admin/signup.html",
        {
            "form": form,
            "username": request.user.username,
            "site_header": "Websocket Service Dashboard",
            "signup_url": reverse_lazy("signup"),
            "login_url": reverse_lazy("dashboard:login"),
        },
    )


def verify_email(request):
    if request.method == "GET":
        verify_code = request.GET.get("verify_code")
        if verify_code:  # verify email
            return render(
                request=request,
                template_name="verify_email_redirect_confirm.html",
                context={
                    "verify_code": verify_code,
                },
            )
        elif request.user.is_authenticated:  # generate new code and send email
            if not request.user.verified:
                if cache.get(f"verify_email_code_{request.user.id}"):
                    messages.warning(
                        request,
                        "You have already requested a verification email. Please check your inbox or spam folder. If you have not received it, please wait a few minutes and try again.",  # noqa: E501
                    )
                else:
                    verify_code = secrets.token_hex(48)
                    cache.set(f"verify_email_code_{request.user.id}", verify_code, 1800)
                    cache.set(f"verify_email_notice_{request.user.id}", True, 30)
                    cache.set(verify_code, request.user.id, 1800)
                    threading.Thread(
                        target=send_verify_email,
                        args=(request, request.user, verify_code),
                    ).start()
                    messages.success(request, f"Verification email sent to {request.user.email}")
                # finally
                try:
                    next = request.GET.get("next")
                    return redirect(next)
                except:
                    return redirect("dashboard:index")
            else:
                raise Http404
        else:
            raise Http404
    elif request.method == "POST":
        try:
            verify_code = request.POST.get("verify_code")
            user_id = cache.get(verify_code)
            user = User.objects.get(id=user_id)
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
            cache.delete(verify_code)
            if request.user.is_authenticated:
                if user == request.user:
                    messages.success(request, "Email verified successfully.")
                else:
                    messages.warning(request, f"Email already verified for {user.username}.")
                return redirect("dashboard:index")
            else:
                messages.success(request, "Email verified successfully.")
                return redirect("dashboard:login")
        except Exception:
            logging.error("Verify email failed. Error: Invalid verify code.")
            messages.error(request, "Verification failed. Make sure you have the correct link.")
            return redirect("dashboard:index")


class PasswordResetView(PasswordContextMixin, FormView):
    form_class = PasswordResetForm
    title = _("Password reset")
    template_name = "registration/password_reset_form.html"
    success_url = reverse_lazy("password_reset_done")

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        try:
            user = User.objects.get(email=email)
            payload = {
                "user_id": user.id,
                "exp": datetime.utcnow() + timedelta(minutes=5),
            }
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
            threading.Thread(
                target=send_password_reset_email,
                args=(self.request, user, token),
            ).start()
        except Exception as e:
            logging.error(f"Password reset failed. Email: {email} Error: {e}")
        return super().form_valid(form)


class PasswordResetConfirmView(PasswordContextMixin, FormView):
    template_name = "registration/password_reset_confirm.html"
    success_url = "/dashboard/"
    form_class = SetPasswordForm
    title = _("Enter new password")

    def dispatch(self, *args, **kwargs):
        self.validlink = False
        self.user = None
        self.token = kwargs.get("token")
        if self.token and not check_token_used(self.token):
            try:
                payload = jwt.decode(self.token, settings.SECRET_KEY, algorithms=["HS256"])
                user_id = payload.get("user_id")
                user = User.objects.get(id=user_id)
                self.user = user
                self.validlink = True
                return super().dispatch(*args, **kwargs)
            except Exception as e:
                logging.error(f"Password reset failed. Error: {e}")
                pass

        # Display the "Password reset unsuccessful" page.
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.validlink:
            context["validlink"] = True
        else:
            context.update(
                {
                    "form": None,
                    "title": _("Password reset unsuccessful"),
                    "validlink": False,
                }
            )
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.user
        return kwargs

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        set_token_used(self.token)
        return super().form_valid(form)
