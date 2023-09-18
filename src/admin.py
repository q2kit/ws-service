from django.contrib import admin

from src.models import Customer, Project


class ProjectInline(admin.TabularInline):
    model = Project
    fields = ("name", "description", "project_id", "secret_key")
    readonly_fields = ("project_id", "secret_key")
    extra = 0


class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "description", "project_id", "secret_key", "created_at", "updated_at")
    fields = ("name", "owner", "description", "project_id", "secret_key", ("created_at", "updated_at"))
    readonly_fields = ("owner", "project_id", "secret_key", "created_at", "updated_at")


class CustomerAdmin(admin.ModelAdmin):
    inlines = [ProjectInline]


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Project, ProjectAdmin)