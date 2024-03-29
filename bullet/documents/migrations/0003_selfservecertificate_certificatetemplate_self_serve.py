# Generated by Django 4.1.3 on 2022-12-02 14:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("competitions", "0025_venue_is_reviewed"),
        ("documents", "0002_certificatetemplate_for_team"),
    ]

    operations = [
        migrations.CreateModel(
            name="SelfServeCertificate",
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
                    "template",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="documents.certificatetemplate",
                    ),
                ),
                (
                    "venue",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="competitions.venue",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="certificatetemplate",
            name="self_serve",
            field=models.ManyToManyField(
                blank=True,
                through="documents.SelfServeCertificate",
                to="competitions.venue",
            ),
        ),
    ]
