from django.forms import ModelForm
from django import forms
from django.core.exceptions import NON_FIELD_ERRORS
from django.contrib.auth.forms import UsernameField
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator

from src.models import Domain, Project, User
from src.funks import validate_domain, validate_project_name, validate_username


class RegistrationForm(forms.Form):
    error_messages = {
        "password_mismatch": _("The two password fields didn't match."),
        "username_exists": _("This username is already in use."),
        "email_exists": _("This email is already in use."),
    }

    username = UsernameField(
        label=_("Username"),
        widget=forms.TextInput(attrs={"autofocus": True, "inputmode": "text"}),
        validators=[MinLengthValidator(3)],
    )
    email = forms.EmailField(label=_("Email"))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(),
        validators=[MinLengthValidator(6)],
    )
    password2 = forms.CharField(
        label=_("Confirm Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"id": "id_password2"}),
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        username, error = validate_username(username)
        if error:
            raise forms.ValidationError(
                error,
                code="invalid_username",
            )
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                self.error_messages["username_exists"],
                code="username_exists",
            )
        
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                self.error_messages["email_exists"],
                code="email_exists",
            )
        
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            self.cleaned_data["password"] = password1
            raise forms.ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
        return password2

        

class DomainForm(ModelForm):
    class Meta:
        model = Domain
        fields = ("domain", "project")
        labels = {
            "domain": "Domain",
        }
        help_texts = {
            "domain": "E.g. example.com, sub.example.com, *.example.com, *.com or localhost",
        }
        error_messages = {
            NON_FIELD_ERRORS: {
                "unique_together": "Domain already exists in this project.",
            },
        }
        widgets = {
            "domain": forms.TextInput(attrs={"autofocus": True, "inputmode": "text"}),
        }


    def clean_domain(self):
        domain = self.cleaned_data.get("domain")
        domain, error = validate_domain(domain)
        if error:
            self.add_error("domain", error)
        
        return domain


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description", "allow_any_domains")
        labels = {
            "name": "Project Name",
            "description": "Description",
            "allow_any_domains": "Allow any domains?",
        }
        help_texts = {
            "name": "Enter project name",
            "description": "Enter project description",
            "allow_any_domains": "Allow any domains, but still exclude blacklisted domains.",
        }
        error_messages = {
            "name": {
                "unique": "Project with this name already exists.",
            },
        }
        widgets = {
            "name": forms.TextInput(attrs={"autofocus": True, "inputmode": "text"}),
        }

    def clean_name(self):
        name = self.cleaned_data.get("name")
        name, error = validate_project_name(name)
        if error:
            self.add_error("name", error)
        self.cleaned_data["name"] = name

        return name


class ProjectFormSuperUser(ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description", "allow_any_domains")
        labels = {
            "name": "Project Name",
            "description": "Description",
            "allow_any_domains": "Allow any domains?",
            "owner": "Owner",
        }
        help_texts = {
            "name": "Enter project name",
            "description": "Enter project description",
            "allow_any_domains": "Allow any domains to access this project",
            "owner": "Select project owner",
        }
        widgets = {
            "name": forms.TextInput(attrs={"autofocus": True, "inputmode": "text"}),
        }


    def clean_name(self):
        name = self.cleaned_data.get("name")
        name, error = validate_project_name(name)
        if error:
            self.add_error("name", error)
        self.cleaned_data["name"] = name
        
        return name


class ProjectAddFormSuperUser(ProjectFormSuperUser):
    class Meta(ProjectFormSuperUser.Meta):
        fields = ("name", "description", "allow_any_domains", "owner")
        
    owner = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=True,
        label=_("Owner"),
        widget=forms.Select(attrs={"class": "form-control"}),
    )


class PasswordResetForm(forms.Form):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )
