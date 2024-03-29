# Generated by Django 4.1.2 on 2022-11-02 22:59

import web.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CertificateTemplate",
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
                    "branch",
                    web.fields.BranchField(
                        choices=[
                            (1, "Náboj Math"),
                            (2, "Náboj Physics"),
                            (3, "Náboj Junior"),
                            (4, "Náboj Chemistry"),
                        ]
                    ),
                ),
                ("template", models.TextField()),
            ],
        ),
    ]
