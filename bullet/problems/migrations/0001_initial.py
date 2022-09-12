# Generated by Django 4.1.1 on 2022-09-12 20:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("competitions", "0016_alter_localizedproblem_unique_together_and_more"),
        ("users", "0010_alter_contestant_team"),
    ]

    operations = [
        migrations.CreateModel(
            name="Problem",
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
                    "competition",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="competitions.competition",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SolvedProblem",
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
                (
                    "problem",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="+",
                        to="problems.problem",
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="solved_problems",
                        to="users.team",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CategoryProblem",
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
                ("number", models.PositiveIntegerField()),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="problems",
                        to="competitions.categorycompetition",
                    ),
                ),
                (
                    "problem",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="category_problems",
                        to="problems.problem",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="categoryproblem",
            constraint=models.UniqueConstraint(
                models.F("problem"),
                models.F("category"),
                models.F("number"),
                name="categoryproblem__problem_category_number",
            ),
        ),
    ]
