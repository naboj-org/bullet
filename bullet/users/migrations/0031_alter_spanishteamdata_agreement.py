# Generated by Django 5.1 on 2024-10-04 18:05

import django.core.validators
from django.db import migrations, models

import users.models.contestants


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0030_alter_emailcampaign_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="spanishteamdata",
            name="agreement",
            field=models.FileField(
                max_length=200,
                upload_to=users.models.contestants.get_spanish_upload,
                validators=[
                    django.core.validators.FileExtensionValidator(["pdf", "zip"])
                ],
            ),
        ),
    ]
