# Generated by Django 4.1.1 on 2022-09-11 12:41

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("education", "0006_school_search"),
        ("users", "0008_alter_team_language"),
    ]

    operations = [
        migrations.RenameModel("Participant", "Contestant"),
    ]
