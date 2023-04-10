# Generated by Django 3.2.7 on 2021-11-21 16:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("web", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Menu",
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
                ("url", models.CharField(max_length=128)),
                (
                    "branch",
                    models.IntegerField(
                        choices=[(1, "Math"), (2, "Physics"), (3, "Junior")]
                    ),
                ),
                ("title", models.CharField(max_length=128)),
            ],
        ),
    ]
