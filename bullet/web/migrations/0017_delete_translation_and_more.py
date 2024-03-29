# Generated by Django 4.0.6 on 2022-07-23 22:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("web", "0016_rename_slug_menu_url"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Translation",
        ),
        migrations.RemoveConstraint(
            model_name="contentblock",
            name="ref_branch_country_lang_unique",
        ),
        migrations.AddField(
            model_name="contentblock",
            name="group",
            field=models.CharField(default="", max_length=256),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name="contentblock",
            constraint=models.UniqueConstraint(
                fields=("group", "reference", "branch", "country", "language"),
                name="content_block__reference_unique",
            ),
        ),
    ]
