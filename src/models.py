from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from src.funks import secret_key_generator

import re


class User(AbstractUser):
    verified = models.BooleanField(default=False)

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
    secret_key = models.CharField(max_length=100, default=secret_key_generator, editable=False)
    allow_any_domains = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.name}"

    def __repr__(self) -> str:
        return f"{self.name}"

    def refresh_secret_key(self):
        self.secret_key = secret_key_generator()
        self.save()

    def check_domain_allowed(self, domain):
        blacklist = self.domains.filter(type=Domain.BLACKLIST).values_list("domain", flat=True)
        blacklist = [re.escape(item).replace(r'\*', r'[a-zA-Z0-9.-]*') for item in blacklist]
        not_in_blacklist = not any(re.match(item, domain) for item in blacklist)
        in_whitelist = Domain.objects.filter(
            domain=domain,
            project=self,
            type=Domain.WHILELIST
        ).exists()
        return not_in_blacklist and (in_whitelist or self.allow_any_domains)


class Domain(models.Model):
    WHILELIST = "whitelist"
    BLACKLIST = "blacklist"
    
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="domains"
    )
    domain = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    type  = models.CharField(
        max_length=10,
        choices=(
            (WHILELIST, "Whitelist"),
            (BLACKLIST, "Blacklist"),
        ),
        default=WHILELIST,
    )

    def __str__(self) -> str:
        return f"{self.project.name} - {self.domain}"

    class Meta:
        unique_together = ("project", "domain")
        ordering = ("-created_at",)
