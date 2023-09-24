from django.utils.html import format_html
from django.utils import timezone
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

import re
from datetime import timedelta
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
import logging


def secret_key_generator(length: int = 32) -> str:
    """
    Generate random secret key
    """
    import secrets

    return secrets.token_urlsafe(length)


def validate_domain(domain: str) -> tuple[str, str]:
    domain = domain.lower()
    if domain.startswith("http://"):
        domain = domain[len("http://") :]
    elif domain.startswith("https://"):
        domain = domain[len("https://") :]
    if domain.endswith("/"):
        domain = domain[:-1]
    if domain == "localhost":
        return domain, None
    if re.match(r"^[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", domain):
        return domain, None
    else:
        return domain, "Invalid domain. (example.com or sub.example.com or localhost)"
    

def validate_project_name(name: str) -> tuple[str, str]:
    if re.match(r"^[a-zA-Z0-9-_]+$", name):
        return name.lower(), None
    else:
        return name, "Invalid name. Must be alphanumeric characters, hyphen or underscore."


def validate_username(username: str) -> tuple[str, str]:
    if re.match(r"^[a-zA-Z0-9-_]+$", username):
        return username.lower(), None
    else:
        return username, "Invalid username. Must be alphanumeric characters, hyphen or underscore."


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
        return format_html(
            '<span title="{}">{}</span>', obj.created_at, calc_time(created_at)
        )
    else:
        return "-"
created_at_display.short_description = "Created At"


def updated_at_display(self, obj=None):
    if obj.updated_at:
        now = timezone.now()
        updated_at = now - obj.updated_at
        return format_html(
            '<span title="{}">{}</span>', obj.updated_at, calc_time(updated_at)
        )
    else:
        return "-"
updated_at_display.short_description = "Updated At"


def send_verify_email(user, token):
    try:
        email = user.email
        username = user.username
        URL_VERIFY = f"https://ws-service.q2k.dev/verify?token={token}"
        ICLOUD_ACCOUNT = os.environ.get("ICLOUD_ACCOUNT")
        ICLOUD_PASS = os.environ.get("ICLOUD_PASS")
        ICLOUD_SENDER = os.environ.get("ICLOUD_SENDER")
        SENDER_NAME = "Websocket Service Team"
        SUBJECT = "Verify your email"
        MESSAGE = f"""
            <html>
                <head></head>
                <body style="font-size: 16px">
                    <p>Hi, {username}</p>
                    <p>Thank you for signing up to Websocket Service.</p>
                    <p>Please click the link below to verify your email address.</p>
                    <a href="{URL_VERIFY}">{URL_VERIFY}</a>
                    <p style="font-size: 13px">This link will expire in 30 minutes.</p>
                    <p style="font-size: 13px"><i>If you did not request this, please ignore this email. Thank you :)</i></p>
                </body>
            </html>
        """

        msg = MIMEMultipart()
        msg["From"] = formataddr((SENDER_NAME, ICLOUD_SENDER))
        msg["To"] = email
        msg["Subject"] = SUBJECT
        msg.attach(MIMEText(MESSAGE, "html"))

        with smtplib.SMTP('smtp.mail.me.com', 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(ICLOUD_ACCOUNT, ICLOUD_PASS)
            smtp.sendmail(ICLOUD_SENDER, email, msg.as_string())
    except Exception as e:
        print(e)
        logging.error(f"Error sending email. Email: {email} Error: {e}")