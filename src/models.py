from django.contrib.auth.models import AbstractUser
from django.db import models

import secrets


class User(AbstractUser):
    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"

    def projects_count(self):
        return self.projects.count()

class Project(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Project Name",
    )
    description = models.CharField(max_length=255, blank=True, null=True)
    owner = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="projects"
    )
    secret_key = models.CharField(max_length=100, default=secrets.token_urlsafe(32), editable=False)
    allow_any_domain = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.name}"

    def __repr__(self) -> str:
        return f"{self.name}"

    def refresh_secret_key(self):
        self.secret_key = secrets.token_urlsafe(32)
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
