# Generated by Django 5.0.1 on 2024-02-08 13:08

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("competitions", "0030_venue_registration_flow_type"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="competition",
            name="name",
        ),
    ]