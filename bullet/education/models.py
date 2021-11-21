from address.models import AddressField
from django.db import models


class SchoolType(models.Model):
    name = models.CharField(max_length=64)
    note = models.CharField(
        max_length=32, help_text="shown in admin interface", blank=True
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

    school_type = models.ForeignKey(SchoolType, on_delete=models.CASCADE)
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

    address = AddressField()
    izo = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name
