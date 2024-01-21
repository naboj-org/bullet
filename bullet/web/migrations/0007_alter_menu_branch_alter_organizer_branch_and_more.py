# Generated by Django 4.0.4 on 2022-06-02 09:13

from django.db import migrations

import web.fields


class Migration(migrations.Migration):
    dependencies = [
        ("web", "0006_alter_menu_order"),
    ]

    operations = [
        migrations.AlterField(
            model_name="menu",
            name="branch",
            field=web.fields.BranchField(
                choices=[
                    (1, "Mathematical Náboj"),
                    (2, "Physics Náboj"),
                    (3, "Náboj Junior"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="organizer",
            name="branch",
            field=web.fields.BranchField(
                choices=[
                    (1, "Mathematical Náboj"),
                    (2, "Physics Náboj"),
                    (3, "Náboj Junior"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="page",
            name="branch",
            field=web.fields.BranchField(
                choices=[
                    (1, "Mathematical Náboj"),
                    (2, "Physics Náboj"),
                    (3, "Náboj Junior"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="partner",
            name="branch",
            field=web.fields.BranchField(
                choices=[
                    (1, "Mathematical Náboj"),
                    (2, "Physics Náboj"),
                    (3, "Náboj Junior"),
                ]
            ),
        ),
    ]
