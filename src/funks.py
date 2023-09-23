from django.utils.html import format_html
from django.utils import timezone

import re
from datetime import timedelta


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
    

def validate_project_name(name: str) -> tuple[str, str]:
    if re.match(r"^[a-zA-Z0-9-_]+$", name):
        return name.lower(), None
    else:
        return name, "Invalid name. Must be alphanumeric characters, hyphen or underscore."



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
