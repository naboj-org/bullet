# Generated by Django 4.0.4 on 2022-06-14 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0014_alter_menu_slug"),
    ]

    operations = [
        migrations.AlterField(
            model_name="menu",
            name="slug",
            field=models.CharField(max_length=128),
        ),
    ]
