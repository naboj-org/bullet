import os
import secrets
import subprocess
import uuid

from django.conf import settings
from django.db import models
from django.template import Context, Template
from django.urls import reverse
from web.fields import BranchField

from documents.generators import prepare_rsvg
from documents.generators.tex_generator import send_to_letter


class SelfServeCertificate(models.Model):
    template = models.ForeignKey("CertificateTemplate", on_delete=models.CASCADE)
    venue = models.OneToOneField("competitions.Venue", on_delete=models.CASCADE)
    # TODO: Languages


class CertificateTemplate(models.Model):
    name = models.CharField(max_length=128)
    for_team = models.BooleanField(default=False)
    branch = BranchField()
    template = models.TextField()
    self_serve = models.ManyToManyField(
        "competitions.Venue", blank=True, through=SelfServeCertificate
    )

    def render(self, context: dict, output_format="pdf") -> bytes:
        template = Template(self.template)
        context = Context(context)
        source = template.render(context)
        env = prepare_rsvg()
        data = subprocess.check_output(
            [
                "rsvg-convert",
                "--format",
                output_format,
                "--dpi-x",
                "300",
                "--dpi-y",
                "300",
            ],
            input=source.encode("utf-8"),
            env=env,
        )
        return data

    def __str__(self):
        return self.name


def tex_template_upload(instance, filename):
    name, ext = os.path.splitext(filename)
    uid = secrets.token_urlsafe(64)
    return os.path.join("tex/templates", f"{uid}{ext}")


class TexTemplate(models.Model):
    class Type(models.TextChoices):
        TEAM_MULTIPLE = ("team_multiple", "Multiple teams")
        TEAM_SINGLE = ("team_single", "Single team")
        GENERIC = ("generic", "Generic")

    competition = models.ForeignKey(
        "competitions.Competition", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=128)
    type = models.CharField(choices=Type, max_length=16)
    template = models.FileField(upload_to=tex_template_upload)
    entrypoint = models.CharField(max_length=128)

    class Meta:
        ordering = ["competition", "name"]

    def __str__(self):
        return self.name


def tex_job_upload(instance, filename):
    name, ext = os.path.splitext(filename)
    return os.path.join("tex/outputs", f"{instance.id}{ext}")


class TexJob(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(TexTemplate, on_delete=models.CASCADE)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    context = models.JSONField(blank=True, default=dict)

    output_file = models.FileField(upload_to=tex_job_upload, blank=True)
    output_log = models.TextField(blank=True)
    output_error = models.CharField(blank=True)
    completed = models.BooleanField(default=False)

    def render(self):
        send_to_letter(
            self.template.template.path,
            self.template.entrypoint,
            self.context,
            reverse("badmin:tex_letter_callback", kwargs={"pk": self.id}),
        )

    def __str__(self):
        return str(self.id)
