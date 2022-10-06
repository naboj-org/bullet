import secrets
import string

from django.conf import settings
from django.db import models
from django.db.models import Max
from phonenumber_field.modelfields import PhoneNumberField
from phonenumbers import PhoneNumberFormat

from bullet import search


class TeamQuerySet(models.QuerySet):
    def competing(self):
        return self.filter(confirmed_at__isnull=False, is_waiting=False)


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

    venue = models.ForeignKey("competitions.Venue", on_delete=models.CASCADE)
    number = models.IntegerField(null=True, blank=True)
    in_school_symbol = models.CharField(max_length=3, null=True, blank=True)

    is_waiting = models.BooleanField(default=False)
    is_reviewed = models.BooleanField(default=False)
    consent_photos = models.BooleanField(default=False)

    objects = TeamQuerySet.as_manager()

    class Meta:
        unique_together = [
            ("venue", "number"),
            ("school", "in_school_symbol"),
        ]

    def __str__(self):
        return f"{self.school} team in {self.venue}"

    @property
    def display_name(self):
        if self.name:
            return self.name
        return str(self.school)

    @property
    def contact_phone_pretty(self):
        if not self.contact_phone:
            return ""
        fmt = self.contact_phone.format_as(PhoneNumberFormat.INTERNATIONAL)
        if not fmt or fmt == "None":
            return self.contact_phone
        return fmt

    def for_search(self):
        return {
            "id": self.id,
            "contact_name": self.contact_name,
            "contact_phone": self.contact_phone_pretty,
            "school": self.school.for_search() if self.school else None,
            "name": self.name,
            "contestants": [c.full_name for c in self.contestants],
        }

    def search_index(self):
        search.client.index("teams").add_documents(
            [self.for_search()],
            "id",
        )

    def save(self, send_to_search=True, *args, **kwargs):
        if not self.secret_link:
            self.secret_link = "".join(
                secrets.choice(string.ascii_lowercase + string.digits)
                for i in range(48)
            )

        if send_to_search:
            self.search_index()

        return super().save(**kwargs)

    def to_waitlist(self):
        self.number = None
        self.is_waiting = True

    def to_competition(self):
        last_number = Team.objects.filter(venue=self.venue).aggregate(Max("number"))[
            "number__max"
        ]
        if not last_number:
            self.number = 1
        else:
            self.number = last_number + 1
        self.is_waiting = False
        # TODO: in_school_symbol


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
        name = self.full_name
        if self.grade:
            name += f" ({self.grade.name})"
        return name
