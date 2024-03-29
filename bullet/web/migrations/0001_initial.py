# Generated by Django 3.2.4 on 2021-07-28 14:10

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Translation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("reference", models.CharField(max_length=256)),
                (
                    "language",
                    models.TextField(
                        choices=[
                            ("sk", "Slovak"),
                            ("cs", "Czech"),
                            ("en-gb", "British English"),
                            ("de-ch", "Swiss German"),
                            ("de-de", "German"),
                            ("fi", "Finnish"),
                            ("pl", "Polish"),
                            ("hu", "Hungarian"),
                            ("ro", "Romanian"),
                            ("ru", "Russian"),
                            ("uk", "Ukrainian"),
                            ("be", "Belarusian"),
                            ("fa", "Persian"),
                        ]
                    ),
                ),
                ("context", models.CharField(blank=True, max_length=128, null=True)),
                ("content", models.TextField(blank=True, null=True)),
            ],
            options={
                "unique_together": {("reference", "language", "context")},
            },
        ),
    ]
