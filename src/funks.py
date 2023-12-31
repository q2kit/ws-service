from django.utils.html import format_html
from django.template.loader import render_to_string
from django.utils import timezone
from django.urls import reverse
from django.core.cache import cache

import re
from datetime import timedelta
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
import logging
import jwt


def secret_key_generator(length: int = 32) -> str:
    """
    Generate random secret key
    """
    import secrets

    return secrets.token_urlsafe(length)


def validate_domain(domain: str) -> tuple[str, str]:
    domain = domain.lower()
    if domain.startswith("http://"):
        domain = domain[len("http://") :]  # noqa: E203
    elif domain.startswith("https://"):
        domain = domain[len("https://") :]  # noqa: E203
    if domain.endswith("/"):
        domain = domain[:-1]
    domain = domain.split(":")[0]
    if re.match(r"^[a-z0-9-]+$", domain):
        if domain == "localhost":
            return domain, None
        else:
            return domain, "E.g. example.com, sub.example.com, *.example.com, *.com or localhost"
    elif re.match(r"^(?:\*\.)?([a-z0-9-]+\.)*([a-z]+)$", domain):
        return domain, None
    else:
        return domain, "E.g. example.com, sub.example.com, *.example.com, *.com or localhost"


def validate_project_name(name: str) -> tuple[str, str]:
    if re.match(r"^[a-zA-Z0-9-_]+$", name):
        return name.lower(), None
    else:
        return name, "Invalid name. Must be alphanumeric characters, hyphen or underscore."


def validate_username(username: str) -> tuple[str, str]:
    if re.match(r"^[a-zA-Z0-9-_]+$", username):
        return username.lower(), None
    else:
        return (
            username,
            "Invalid username. Must be alphanumeric characters, hyphen or underscore.",
        )


def calc_time(time: timedelta) -> str:
    """
    Calculate time from timedelta object
    Example:
        time = timedelta(days=1, hours=2, minutes=3, seconds=4)
        calc_time(time) -> "1 day ago"
        ---
        time = timedelta(days=0, hours=2, minutes=3, seconds=4)
        calc_time(time) -> "2 hours ago"
    """

    years = time.days // 365
    months = time.days // 30
    weeks = time.days // 7
    days = time.days
    hours = time.seconds // 3600
    minutes = time.seconds // 60
    seconds = time.seconds

    time_dict = {
        "year": years,
        "month": months,
        "week": weeks,
        "day": days,
        "hour": hours,
        "minute": minutes,
        "second": seconds,
    }

    for key, value in time_dict.items():
        if value > 0:
            if value == 1:
                return f"{value} {key} ago"
            else:
                return f"{value} {key}s ago"
    else:
        return "Just now"


def created_at_display(self, obj=None):
    if obj.created_at:
        now = timezone.now()
        created_at = now - obj.created_at
        return format_html('<span title="{}">{}</span>', obj.created_at, calc_time(created_at))
    else:
        return "-"


created_at_display.short_description = "Created At"


def updated_at_display(self, obj=None):
    if obj.updated_at:
        now = timezone.now()
        updated_at = now - obj.updated_at
        return format_html('<span title="{}">{}</span>', obj.updated_at, calc_time(updated_at))
    else:
        return "-"


updated_at_display.short_description = "Updated At"


def send_verify_email(request, user, verify_code):
    try:
        email = user.email
        username = user.username
        SERVER_HOST = f"{request.scheme}://{request.get_host()}"
        VERIFY_URL = f"{SERVER_HOST}{reverse('verify')}?verify_code={verify_code}"
        SMTP_HOST = os.environ.get("SMTP_HOST")
        SMTP_PORT = os.environ.get("SMTP_PORT")
        SMTP_ACCOUNT = os.environ.get("SMTP_ACCOUNT")
        SMTP_PASS = os.environ.get("SMTP_PASS")
        SMTP_SENDER = os.environ.get("SMTP_SENDER")
        SENDER_NAME = os.environ.get("SENDER_NAME")
        SUBJECT = "Verify your email"
        context = {
            "SERVER_HOST": SERVER_HOST,
            "VERIFY_URL": VERIFY_URL,
            "username": username,
        }
        MESSAGE = render_to_string("verify_email_template.html", context)

        msg = MIMEMultipart()
        msg["From"] = formataddr((SENDER_NAME, SMTP_SENDER))
        msg["To"] = email
        msg["Subject"] = SUBJECT
        msg.attach(MIMEText(MESSAGE, "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(SMTP_ACCOUNT, SMTP_PASS)
            smtp.sendmail(SMTP_SENDER, email, msg.as_string())
    except Exception as e:
        logging.error(f"Error sending verify email. Email: {email} Error: {e}")


def send_password_reset_email(request, user, token):
    try:
        email = user.email
        username = user.username
        SERVER_HOST = f"{request.scheme}://{request.get_host()}"
        RESET_URL = f"{SERVER_HOST}{reverse('password_reset_confirm', kwargs={'token': token})}"
        SMTP_HOST = os.environ.get("SMTP_HOST")
        SMTP_PORT = os.environ.get("SMTP_PORT")
        SMTP_ACCOUNT = os.environ.get("SMTP_ACCOUNT")
        SMTP_PASS = os.environ.get("SMTP_PASS")
        SMTP_SENDER = os.environ.get("SMTP_SENDER")
        SENDER_NAME = os.environ.get("SENDER_NAME")
        SUBJECT = "Reset your password"
        context = {
            "SERVER_HOST": SERVER_HOST,
            "RESET_URL": RESET_URL,
            "username": username,
        }
        MESSAGE = render_to_string("password_reset_email_template.html", context)

        msg = MIMEMultipart()
        msg["From"] = formataddr((SENDER_NAME, SMTP_SENDER))
        msg["To"] = email
        msg["Subject"] = SUBJECT
        msg.attach(MIMEText(MESSAGE, "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(SMTP_ACCOUNT, SMTP_PASS)
            smtp.sendmail(SMTP_SENDER, email, msg.as_string())
    except Exception as e:
        logging.error(f"Error sending password reset email. Email: {email} Error: {e}")


def check_token_used(token):
    return cache.get(f"token_used_{token}")


def set_token_used(token):
    expiration = jwt.decode(token, options={"verify_signature": False})["exp"]
    now = timezone.now().timestamp()
    cache.set(f"token_used_{token}", True, timeout=expiration - now)
