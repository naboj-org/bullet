from django.db import models
from django.db.models import Q
from django_countries.fields import CountryField
from users.models import Team
from web.fields import ChoiceArrayField, LanguageField


class EmailCampaign(models.Model):
    class StatusChoices(models.TextChoices):
        UNCONFIRMED = "U", "Unconfirmed"
        REGISTERED = "R", "Registered"
        WAITINGLIST = "W", "Waiting list"
        CHECKEDIN = "C", "Checked in"

    competition = models.ForeignKey(
        "competitions.Competition", on_delete=models.CASCADE
    )
    subject = models.CharField(max_length=128)
    template = models.TextField(blank=True)
    last_sent = models.DateTimeField(blank=True, null=True)

    team_countries = ChoiceArrayField(CountryField(), blank=True)
    team_languages = ChoiceArrayField(LanguageField(), blank=True)
    team_venues = models.ManyToManyField(
        "competitions.Venue", blank=True, related_name="+"
    )
    team_statuses = ChoiceArrayField(
        models.CharField(max_length=1, choices=StatusChoices.choices), blank=True
    )

    @property
    def teams(self):
        qs = Team.objects.filter(
            venue__category_competition__competition=self.competition
        )
        if self.team_countries:
            qs = qs.filter(venue__country__in=self.team_countries)
        if self.team_languages:
            qs = qs.filter(language__in=self.team_languages)
        if self.team_venues.exists():
            qs = qs.filter(venue__in=self.team_venues.all())
        if self.team_statuses:
            q = Q()
            if EmailCampaign.StatusChoices.UNCONFIRMED in self.team_statuses:
                q.add(Q(confirmed_at__isnull=True), Q.OR)
            if EmailCampaign.StatusChoices.REGISTERED in self.team_statuses:
                q.add(
                    Q(
                        confirmed_at__isnull=False,
                        is_waiting=False,
                        is_checked_in=False,
                    ),
                    Q.OR,
                )
            if EmailCampaign.StatusChoices.WAITINGLIST in self.team_statuses:
                q.add(Q(is_waiting=True), Q.OR)
            if EmailCampaign.StatusChoices.CHECKEDIN in self.team_statuses:
                q.add(Q(is_checked_in=True), Q.OR)
            qs = qs.filter(q)

        return qs
