import hashlib

from django.db import models

from src.funks import hex_uuid


class Customer(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.email

    def __repr__(self) -> str:
        return self.email

    def check_password(self, password: str) -> bool:
        return self.password == hashlib.sha256(password.encode()).hexdigest()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.password = hashlib.sha256(self.password.encode()).hexdigest()
        super().save(*args, **kwargs)

    @property
    def projects_count(self) -> int:
        return self.projects.count()


class Project(models.Model):
    id = models.CharField(
        max_length=100,
        primary_key=True,
        default=hex_uuid,
        editable=False,
        verbose_name="Project ID",
    )
    secret_key = models.CharField(max_length=100, default=hex_uuid, editable=False)
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="projects"
    )
    description = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.id} - {self.name}"

    def __repr__(self) -> str:
        return f"{self.id} - {self.name}"

    def _get_project_id_val(self, meta=None):
        return self.id

    def _set_project_id_val(self, value):
        self.id = value

    project_id = property(_get_project_id_val, _set_project_id_val)
    project_id.fget.short_description = "Project ID"

    def refresh_secret_key(self):
        self.secret_key = hex_uuid()
        self.save()


class Domain(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="domains"
    )
    domain = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.project.name} - {self.domain}"

    class Meta:
        unique_together = ("project", "domain")
        ordering = ("-created_at",)
