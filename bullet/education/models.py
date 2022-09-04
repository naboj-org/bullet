from django.db import models
from django_countries.fields import CountryField


class SchoolType(models.Model):
    name = models.CharField(max_length=64)
    note = models.CharField(
        max_length=32, help_text="shown in admin interface", blank=True
    )
    identifier = models.CharField(
        max_length=32,
        help_text="used in school importers",
        blank=True,
        null=True,
        unique=True,
    )

    def __str__(self):
        return f"{self.name} ({self.note})"


class Grade(models.Model):
    class Meta:
        ordering = (
            "school_type",
            "order",
        )
        unique_together = ("school_type", "order")

    school_type = models.ForeignKey(
        SchoolType, on_delete=models.CASCADE, related_name="grades"
    )
    name = models.CharField(max_length=64)
    order = models.IntegerField()

    def __str__(self):
        return f"{self.school_type} / {self.name}"


class Education(models.Model):
    name = models.CharField(max_length=64)
    grades = models.ManyToManyField(Grade)

    def __str__(self):
        return self.name


class School(models.Model):
    name = models.CharField(max_length=256)
    types = models.ManyToManyField(SchoolType)
    address = models.CharField(max_length=256, blank=True, null=True)
    country = CountryField()

    importer = models.CharField(max_length=16, blank=True, null=True)
    importer_identifier = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                "importer",
                "importer_identifier",
                name="school__importer_importer_identifier",
            ),
        )

    def __str__(self):
        return self.name
