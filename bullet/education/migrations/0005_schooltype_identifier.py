# Generated by Django 4.0.7 on 2022-09-04 09:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("education", "0004_remove_school_izo_school_importer_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="schooltype",
            name="identifier",
            field=models.CharField(
                blank=True,
                help_text="used in school importers",
                max_length=32,
                null=True,
                unique=True,
            ),
        ),
    ]
