# Generated by Django 4.1.10 on 2023-09-15 19:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("education", "0008_school_is_hidden"),
    ]

    operations = [
        migrations.AddField(
            model_name="school",
            name="is_legacy",
            field=models.BooleanField(default=False),
        ),
    ]