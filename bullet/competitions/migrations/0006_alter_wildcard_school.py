# Generated by Django 3.2.7 on 2021-11-21 12:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("education", "0001_initial"),
        ("competitions", "0005_alter_categorycompetition_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="wildcard",
            name="school",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="education.school"
            ),
        ),
    ]
