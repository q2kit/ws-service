from django.forms import ModelForm
from django.core.exceptions import NON_FIELD_ERRORS

from src.models import Domain
from src.funks import validate_domain


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
