# Generated by Django 4.1.1 on 2022-09-24 13:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("countries", "0005_alter_branchcountry_languages"),
    ]

    operations = [
        migrations.AddField(
            model_name="branchcountry",
            name="email",
            field=models.EmailField(default="", max_length=254),
            preserve_default=False,
        ),
    ]
