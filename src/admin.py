from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from src.models import Customer, Project


class ProjectInline(admin.TabularInline):
    model = Project
    fields = ("name", "description", "project_id", "secret_key")
    readonly_fields = ("project_id", "secret_key")
    extra = 0


class ProjectAdmin(admin.ModelAdmin):
    sortable_by = ("name", "owner", "created_at", "updated_at")
    list_display = ("name", "project_id", "secret_key", "owner_display", "description", "created_at", "updated_at")
    search_fields = ("name", "owner__email", "id", "secret_key")
    list_filter = ("owner",)
    list_select_related = ("owner",)

    def owner_display(self, obj):
        link = reverse("admin:src_customer_change", args=[obj.owner.id])
        return format_html('<b><a href="{}">{}</a></b>', link, obj.owner.email)
    owner_display.short_description = "Owner"

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("owner_display", "project_id", "secret_key", "created_at", "updated_at")
        else:
            return ("project_id", "secret_key")
        
    def get_fields(self, request, obj=None):
        if obj:
            return ("name", "owner_display", "description", "project_id", "secret_key", ("created_at", "updated_at"))
        else:
            return ("name", "owner", "description")

class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "projects_count", "created_at", "updated_at")
    search_fields = ("email", "id")
    inlines = [ProjectInline]


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Project, ProjectAdmin)