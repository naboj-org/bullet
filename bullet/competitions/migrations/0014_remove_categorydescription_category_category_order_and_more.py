# Generated by Django 4.1 on 2022-08-04 21:23

import django_countries.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("competitions", "0013_rename_competitionsite_competitionvenue_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="categorydescription",
            name="category",
        ),
        migrations.AddField(
            model_name="category",
            name="order",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="category",
            name="slug",
            field=models.SlugField(default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="venue",
            name="country",
            field=django_countries.fields.CountryField(default="SK", max_length=2),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name="category",
            constraint=models.UniqueConstraint(
                models.F("branch"), models.F("slug"), name="category__branch_slug"
            ),
        ),
        migrations.DeleteModel(
            name="CategoryDescription",
        ),
    ]
