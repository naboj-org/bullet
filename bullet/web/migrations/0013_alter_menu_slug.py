# Generated by Django 4.0.4 on 2022-06-14 14:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("web", "0012_menu_is_external"),
    ]

    operations = [
        migrations.AlterField(
            model_name="menu",
            name="slug",
            field=models.URLField(max_length=128),
        ),
    ]
