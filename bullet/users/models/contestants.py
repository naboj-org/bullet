import secrets
import string

from django.conf import settings
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Team(models.Model):
    contact_name = models.CharField(max_length=256)
    contact_email = models.EmailField()
    contact_phone = PhoneNumberField(null=True, blank=True)
    secret_link = models.CharField(max_length=48, unique=True)

    school = models.ForeignKey(
        "education.School", on_delete=models.CASCADE, blank=True, null=True
    )
    name = models.CharField(max_length=128, blank=True, null=True)
    language = models.TextField(blank=True, choices=settings.LANGUAGES)

    registered_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    competition_venue = models.ForeignKey(
        "competitions.CompetitionVenue", on_delete=models.CASCADE
    )
    number = models.IntegerField(null=True, blank=True)
    in_school_symbol = models.CharField(max_length=3, null=True, blank=True)

    is_reviewed = models.BooleanField(default=False)

    class Meta:
        unique_together = [
            ("competition_venue", "number"),
            ("school", "in_school_symbol"),
        ]

    def __str__(self):
        return f"{self.school} team in {self.competition_venue}"

    @property
    def display_name(self):
        if self.name:
            return self.name
        return str(self.school)

    def save(self, *args, **kwargs):
        if not self.secret_link:
            self.secret_link = "".join(
                secrets.choice(string.ascii_lowercase + string.digits)
                for i in range(48)
            )
        super().save(*args, **kwargs)


class Contestant(models.Model):
    team = models.ForeignKey(
        "users.Team", on_delete=models.CASCADE, related_name="contestants"
    )

    full_name = models.CharField(max_length=256)
    grade = models.ForeignKey(
        "education.Grade",
        on_delete=models.CASCADE,
        related_name="+",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.full_name
