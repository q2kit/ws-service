from django.utils.html import format_html
from django.utils import timezone

import re
from datetime import timedelta
from uuid import uuid4


def validate_email(email: str) -> bool:
    if re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
        return True, None
    else:
        return False, "Invalid email"


def validate_password(password: str) -> bool:
    if len(password) >= 6:
        return True, None
    else:
        return False, "Password must be at least 6 characters"


def validate_domain(domain: str) -> tuple[str, str]:
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


def hex_uuid():
    return uuid4().hex


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
