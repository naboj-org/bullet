import secrets
import string

from django.conf import settings
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from phonenumbers import PhoneNumberFormat
from users.emails.teams import send_to_competition_email

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
    is_checked_in = models.BooleanField(default=False)
    is_reviewed = models.BooleanField(default=False)
    consent_photos = models.BooleanField(default=False)

    objects = TeamQuerySet.as_manager()

    class Meta:
        unique_together = [
            ("venue", "number"),
            ("venue", "school", "in_school_symbol"),
        ]

    def __str__(self):
        return self.display_name

    @property
    def code(self):
        return f"{self.venue.shortcode}{self.number:03d}"

    @property
    def display_name(self):
        if self.name:
            return self.name
        if self.in_school_symbol:
            return f"{self.school} {self.in_school_symbol}"
        return f"{self.school}"

    @property
    def contact_phone_pretty(self):
        if not self.contact_phone:
            return ""
        fmt = self.contact_phone.format_as(PhoneNumberFormat.INTERNATIONAL)
        if not fmt or fmt == "None":
            return str(self.contact_phone)
        return fmt

    @property
    def contestants_names(self):
        return ", ".join([c.full_name for c in self.contestants.all()])

    @property
    def id_display(self):
        return f"#{self.id:06d}"

    def for_search(self):
        return {
            "id": self.id,
            "competition": self.venue.category_competition.competition_id,
            "contact_name": self.contact_name,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone_pretty,
            "school": self.school.for_search() if self.school else None,
            "name": self.name,
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

        x = super().save(**kwargs)

        if send_to_search:
            self.search_index()

        return x

    def delete(self, using=None, keep_parents=False):
        search.client.index("teams").delete_document(self.id)
        return super().delete(using, keep_parents)

    def to_waitlist(self):
        self.number = None
        self.in_school_symbol = None
        self.is_waiting = True

    def to_competition(self, send_email=True):
        self.is_waiting = False
        if send_email:
            send_to_competition_email(self)


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
