# Generated by Django 4.1.1 on 2022-10-02 20:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0020_menu_is_visible"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="logo",
            options={"ordering": ("name",)},
        ),
    ]