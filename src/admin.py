from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone

from src.funks import created_at_display, updated_at_display
from src.models import Customer, Project, Domain
from src.forms import DomainForm


class ProjectInline(admin.TabularInline):
    model = Project
    fields = (
        "name",
        "description",
        "get_project_id_display",
        "get_secret_key_display",
        "created_at_display",
    )
    readonly_fields = (
        "get_project_id_display",
        "get_secret_key_display",
        "created_at_display",
    )
    extra = 0
    ordering = ("created_at",)
    show_change_link = True
    created_at_display = created_at_display

    def get_project_id_display(self, obj=None):
        if obj.name:
            return obj.project_id
        else:
            return "-"

    get_project_id_display.short_description = "Project ID"

    def get_secret_key_display(self, obj=None):
        if obj.name:
            return obj.secret_key
        else:
            return "-"

    get_secret_key_display.short_description = "Secret Key"


class DomainInline(admin.TabularInline):
    model = Domain
    fields = ("domain", "project", "created_at_display", "updated_at_display")
    readonly_fields = ("created_at_display", "updated_at_display")
    extra = 0
    ordering = ("created_at",)
    show_change_link = True
    created_at_display = created_at_display
    updated_at_display = updated_at_display
    form = DomainForm
    verbose_name = "Whitelisted Domain"


class ProjectAdmin(admin.ModelAdmin):
    sortable_by = ("name", "owner", "created_at", "updated_at")
    list_display = (
        "name",
        "project_id",
        "secret_key_display",
        "owner_display",
        "created_at_display",
    )
    search_fields = ("name", "owner__email", "id", "secret_key")
    list_filter = ("owner",)
    list_select_related = ("owner",)
    ordering = ("-created_at",)
    list_display_links = ("name", "project_id")
    inlines = [DomainInline]
    created_at_display = created_at_display

    def owner_display(self, obj):
        link = reverse("admin:src_customer_change", args=[obj.owner.id])
        return format_html('<b><a href="{}">{}</a></b>', link, obj.owner.email)

    owner_display.short_description = "Owner"

    def secret_key_display(self, obj):
        return format_html(
            '<span title="{}">{}</span>', obj.secret_key, obj.secret_key[:10] + "..."
        )

    secret_key_display.short_description = "Secret Key"

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return (
                "owner_display",
                "project_id",
                "secret_key",
                "created_at",
                "updated_at",
            )
        else:
            return ("project_id", "secret_key")

    def get_fields(self, request, obj=None):
        if obj:
            return (
                "name",
                "owner_display",
                "description",
                "project_id",
                "secret_key",
                ("created_at", "updated_at"),
            )
        else:
            return ("name", "owner", "description")


class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "projects_count", "created_at", "updated_at")
    search_fields = ("email", "id")
    inlines = [ProjectInline]
    list_display_links = ("id", "email")

    def get_fields(self, request, obj=None):
        if obj:
            return ("email", "password", ("created_at", "updated_at"))
        else:
            return ("email", "password")

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("email", "password", "created_at", "updated_at")
        else:
            return ()


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Project, ProjectAdmin)
