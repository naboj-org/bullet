# Generated by Django 4.1.2 on 2022-10-23 10:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("problems", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ScannerLog",
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
                ("barcode", models.CharField(max_length=32)),
                (
                    "result",
                    models.IntegerField(
                        choices=[(0, "Ok"), (1, "Scan Err"), (2, "Integrity Err")]
                    ),
                ),
                ("message", models.CharField(blank=True, max_length=128)),
                ("timestamp", models.DateTimeField()),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
