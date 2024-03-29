# Generated by Django 4.1.3 on 2022-11-05 19:12

import web.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0019_alter_team_unique_together"),
    ]

    operations = [
        migrations.AlterField(
            model_name="emailcampaign",
            name="team_statuses",
            field=web.fields.ChoiceArrayField(
                base_field=models.CharField(
                    choices=[
                        ("U", "Unconfirmed"),
                        ("R", "Registered"),
                        ("W", "Waiting list"),
                        ("C", "Checked in"),
                        ("K", "Reviewed"),
                    ],
                    max_length=1,
                ),
                blank=True,
                size=None,
            ),
        ),
    ]
