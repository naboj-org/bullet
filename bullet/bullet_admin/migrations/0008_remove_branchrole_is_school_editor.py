# Generated by Django 5.0.3 on 2024-03-15 15:05

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("bullet_admin", "0007_branchrole_is_photograph"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="branchrole",
            name="is_school_editor",
        ),
    ]
