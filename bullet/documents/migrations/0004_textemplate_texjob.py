# Generated by Django 5.0.3 on 2024-04-11 15:14

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import documents.models


class Migration(migrations.Migration):
    dependencies = [
        ("competitions", "0032_wildcard_category_alter_wildcard_competition"),
        ("documents", "0003_selfservecertificate_certificatetemplate_self_serve"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="TexTemplate",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=128)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("team_multiple", "Multiple teams"),
                            ("team_single", "Single team"),
                            ("generic", "Generic"),
                        ],
                        max_length=16,
                    ),
                ),
                (
                    "template",
                    models.FileField(upload_to=documents.models.tex_template_upload),
                ),
                ("entrypoint", models.CharField(max_length=128)),
                (
                    "competition",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="competitions.competition",
                    ),
                ),
            ],
            options={
                "ordering": ["competition", "name"],
            },
        ),
        migrations.CreateModel(
            name="TexJob",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("context", models.JSONField(blank=True, default=dict)),
                (
                    "output_file",
                    models.FileField(
                        blank=True, upload_to=documents.models.tex_job_upload
                    ),
                ),
                ("output_log", models.TextField(blank=True)),
                ("output_error", models.CharField(blank=True, max_length=256)),
                ("completed", models.BooleanField(default=False)),
                (
                    "creator",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "template",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="documents.textemplate",
                    ),
                ),
            ],
        ),
    ]
