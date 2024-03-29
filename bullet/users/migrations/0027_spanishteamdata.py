# Generated by Django 4.1.10 on 2023-09-27 15:09

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models

import users.models.contestants


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0026_alter_historicalteam_language_alter_team_language"),
    ]

    operations = [
        migrations.CreateModel(
            name="SpanishTeamData",
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
                (
                    "agreement",
                    models.FileField(
                        upload_to=users.models.contestants.get_spanish_upload,
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                ["pdf", "zip"]
                            )
                        ],
                    ),
                ),
                ("is_verified", models.BooleanField(default=False)),
                (
                    "team",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="spanish_data",
                        to="users.team",
                    ),
                ),
            ],
        ),
    ]
