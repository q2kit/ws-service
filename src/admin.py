from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from src.funks import created_at_display, updated_at_display
from src.models import User, Project, Domain
from src.forms import DomainForm, ProjectForm, ProjectFormSuperUser, ProjectAddFormSuperUser


class ProjectInline(admin.TabularInline):
    model = Project
    fields = (
        "name",
        "description",
        "get_secret_key_display",
        "created_at_display",
    )
    readonly_fields = (
        "get_secret_key_display",
        "created_at_display",
    )
    extra = 0
    ordering = ("created_at",)
    show_change_link = True
    created_at_display = created_at_display

    def get_secret_key_display(self, obj=None):
        if obj:
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
    class Media:
        css = {
            "all": (
                "css/refresh_secret_key.css",
                "css/fontawesome.css",
            )
        }
        js = (
            "js/refresh_secret_key.js",
            "js/fontawesome.js"
        )

    list_select_related = ("owner",)
    ordering = ("-created_at",)
    list_display_links = ("name",)
    inlines = [DomainInline]
    created_at_display = created_at_display
    updated_at_display = updated_at_display

    def get_queryset(self, request):
        if request.user.is_superuser:
            return Project.objects.all()
        else:
            return Project.objects.filter(owner=request.user)
        
    def save_model(self, request, obj, form, change):
        if not change: # create
            if not obj.owner:
                obj.owner = request.user
        obj.save()

    def get_sortable_by(self, request):
        if request.user.is_superuser:
            return ("name", "owner", "created_at", "updated_at")
        else:
            return ("name", "created_at", "updated_at")
        
    def get_list_display(self, request):
        if request.user.is_superuser:
            return (
                "name",
                "secret_key_display",
                "owner_display",
                "created_at_display",
                "updated_at_display",
            )
        else:
            return (
                "name",
                "secret_key_display",
                "created_at_display",
                "updated_at_display",
            )

    def get_search_fields(self, request):
        if request.user.is_superuser:
            return ("name", "owner__email", "owner__username")
        else:
            return ("name",)
        
    def get_list_filter(self, request):
        if request.user.is_superuser:
            return ("owner",)
        else:
            return ()
        
    def get_fields(self, request, obj=None):
        if request.user.is_superuser:
            if obj:
                return (
                    "name",
                    "owner_display",
                    "description",
                    "secret_key",
                    "allow_any_domain",
                    ("created_at", "updated_at"),
                )
            else:
                return ("name", "owner", "description", "allow_any_domain")
        else:
            if obj:
                return (
                    "name",
                    "description",
                    "secret_key",
                    "allow_any_domain",
                    ("created_at", "updated_at"),
                )
            else:
                return ("name", "description", "allow_any_domain")
            
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            if obj:
                return (
                    "owner_display",
                    "secret_key",
                    "created_at",
                    "updated_at",
                )
            else:
                return ("secret_key",)
        else:
            if obj:
                return (
                    "secret_key",
                    "created_at",
                    "updated_at",
                )
            else:
                return ("secret_key",)
            
    def get_form(self, request, obj=None, **kwargs):
        if request.user.is_superuser:
            if obj:
                return ProjectFormSuperUser
            else:
                return ProjectAddFormSuperUser
        else:
            return ProjectForm

    def owner_display(self, obj):
        if obj.owner:
            link = reverse("admin:src_user_change", args=[obj.owner.id])
            return format_html('<b><a href="{}">{}</a></b>', link, obj.owner.username)
        else:
            return "-"

    owner_display.short_description = "Owner"

    def secret_key_display(self, obj):
        return format_html(
            '<span title="{}">{}</span>', obj.secret_key, obj.secret_key[:10] + "..."
        )

    secret_key_display.short_description = "Secret Key"


class CustomUserAdmin(admin.ModelAdmin):
    add_form_template = "admin/auth/user/add_form.html"
    list_display = ("id", "username", "email", "projects_count", "date_joined")
    search_fields = ("username",)
    inlines = [ProjectInline]
    list_display_links = ("id", "username")

    def get_fields(self, request, obj=None):
        if obj:
            return ("username", "password", "email", "verified")
        else:
            return ("username", "password", "email", "verified")

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("username", "password", "date_joined")
        else:
            return ()

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.set_password(form.cleaned_data["password"])
            obj.username = form.cleaned_data["username"].lower()
            obj.is_active = True
            obj.is_staff = True
        if request.user.is_superuser and obj.verified:
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
            obj.user_permissions.set(permission)

        obj.save()

admin.site.unregister(Group)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Project, ProjectAdmin)
