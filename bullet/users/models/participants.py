from address.models import AddressField
from django.db import models
from django.db.models import IntegerChoices
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from bullet.constants import Languages


class School(models.Model):
    class SchoolType(IntegerChoices):
        # TODO all school types
        HIGH_SCHOOL = 1, _("High school")
        ELEMENTARY_SCHOOL = 2, _("Elementary school")

    name = models.CharField(max_length=256)
    type = models.IntegerField(choices=SchoolType.choices)

    address = AddressField()
    izo = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class Team(models.Model):
    contact_name = models.CharField(max_length=256)
    contact_email = models.EmailField()
    contact_phone = PhoneNumberField(null=True, blank=True)
    secret_link = models.CharField(max_length=48, unique=True)

    school = models.ForeignKey("users.School", on_delete=models.CASCADE)
    language = models.TextField(choices=Languages.choices)

    registered_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    competition_site = models.ForeignKey(
        "competitions.CompetitionSite", on_delete=models.CASCADE
    )
    number = models.IntegerField(null=True, blank=True)
    in_school_symbol = models.CharField(max_length=1, null=True, blank=True)

    is_official = models.BooleanField(default=True)

    is_reviewed = models.BooleanField(default=False)

    class Meta:
        unique_together = [
            ("competition_site", "number"),
            ("school", "in_school_symbol"),
        ]

    def __str__(self):
        return f"{self.school} team in {self.competition_site}"


class Participant(models.Model):
    team = models.ForeignKey(
        "users.Team", on_delete=models.CASCADE, related_name="participants"
    )

    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    graduation_year = models.IntegerField()
    birth_year = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.graduation_year})"
