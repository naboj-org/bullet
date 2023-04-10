# Generated by Django 4.1.1 on 2022-09-20 16:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("competitions", "0017_alter_localizedproblem_unique_together_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="categorycompetition",
            name="max_members_per_team",
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="categorycompetition",
            name="max_teams_per_school",
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="categorycompetition",
            name="max_teams_second_round",
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="categorycompetition",
            name="problems_per_team",
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
