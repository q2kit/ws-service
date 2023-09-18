from django.contrib import admin

from src.models import Customer, Project


class ProjectInline(admin.TabularInline):
    model = Project
    fields = ("name", "description", "project_id", "secret_key")
    readonly_fields = ("project_id", "secret_key")
    extra = 0


class ProjectAdmin(admin.ModelAdmin):
    sortable_by = ("name", "owner", "created_at", "updated_at")
    list_display = ("name", "project_id", "secret_key", "owner", "description", "created_at", "updated_at")
    fields = ("name", "owner", "description", "project_id", "secret_key", ("created_at", "updated_at"))
    readonly_fields = ("owner", "project_id", "secret_key", "created_at", "updated_at")
    search_fields = ("name", "owner__email", "id", "secret_key")
    list_filter = ("owner",)
    list_select_related = ("owner",)

class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "projects_count", "created_at", "updated_at")
    search_fields = ("email", "id")
    inlines = [ProjectInline]


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Project, ProjectAdmin)