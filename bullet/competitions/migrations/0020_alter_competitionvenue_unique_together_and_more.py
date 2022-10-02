# Generated by Django 4.1.1 on 2022-09-29 19:03

import django_countries.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bullet_admin", "0003_alter_competitionrole_venue"),
        ("competitions", "0019_remove_competitionvenue_email_alias_and_more"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="competitionvenue",
            unique_together=set(),
        ),
        migrations.AddField(
            model_name="competitionvenue",
            name="address",
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AddField(
            model_name="competitionvenue",
            name="country",
            field=django_countries.fields.CountryField(default="SK", max_length=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="competitionvenue",
            name="is_online",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="competitionvenue",
            name="name",
            field=models.CharField(default="Venue", max_length=256),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="competitionvenue",
            name="shortcode",
            field=models.CharField(default="SK", max_length=6),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name="competitionvenue",
            unique_together={("category_competition", "shortcode")},
        ),
        migrations.RemoveField(
            model_name="competitionvenue",
            name="venue",
        ),
        migrations.DeleteModel(
            name="Venue",
        ),
    ]