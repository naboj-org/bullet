# Generated by Django 3.2.7 on 2021-11-21 13:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("education", "0001_initial"),
        ("competitions", "0006_alter_wildcard_school"),
    ]

    operations = [
        migrations.AddField(
            model_name="categorycompetition",
            name="educations",
            field=models.ManyToManyField(to="education.Education"),
        ),
    ]
