from django.forms import ModelForm
from django.core.exceptions import NON_FIELD_ERRORS

from src.models import Domain, Project
from src.funks import validate_domain, validate_project_name


class DomainForm(ModelForm):
    class Meta:
        model = Domain
        fields = ("domain", "project")
        labels = {
            "domain": "Domain",
        }
        help_texts = {
            "domain": "Enter domain name",
        }
        error_messages = {
            NON_FIELD_ERRORS: {
                "unique_together": "Domain already exists in this project.",
            },
        }

    def clean(self):
        domain = self.cleaned_data.get("domain")
        domain, error = validate_domain(domain)
        if error:
            self.add_error("domain", error)
        self.cleaned_data["domain"] = domain
        return super().clean()


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description", "allow_any_domain")
        labels = {
            "name": "Project Name",
            "description": "Description",
            "allow_any_domain": "Allow Any Domain",
        }
        help_texts = {
            "name": "Enter project name",
            "description": "Enter project description",
            "allow_any_domain": "Allow any domain to access this project",
        }

    def clean(self):
        name = self.cleaned_data.get("name")
        name, error = validate_project_name(name)
        if error:
            self.add_error("name", error)
        return super().clean()


class ProjectFormSuperUser(ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description", "allow_any_domain", "owner")
        labels = {
            "name": "Project Name",
            "description": "Description",
            "allow_any_domain": "Allow Any Domain",
            "owner": "Owner",
        }
        help_texts = {
            "name": "Enter project name",
            "description": "Enter project description",
            "allow_any_domain": "Allow any domain to access this project",
            "owner": "Select project owner",
        }