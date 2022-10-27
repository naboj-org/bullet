# Generated by Django 4.1.2 on 2022-10-24 20:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0017_team_is_checked_in"),
        ("problems", "0002_scannerlog"),
    ]

    operations = [
        migrations.CreateModel(
            name="ResultRow",
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
                ("competition_time", models.DurationField()),
                ("solved_problems", models.BinaryField()),
                ("solved_count", models.IntegerField()),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="users.team",
                    ),
                ),
            ],
        ),
    ]