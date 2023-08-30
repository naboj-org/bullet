from competitions.branches import Branches
from countries.utils import country_reverse
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Count
from django.template import Context, Template
from django_countries.fields import CountryField
from users.emails.teams import TeamCountry
from users.models import Team, TeamStatus
from web.fields import ChoiceArrayField, LanguageField

from bullet.utils.email import send_email


class EmailCampaign(models.Model):
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
        models.CharField(max_length=1, choices=TeamStatus.choices), blank=True
    )
    team_contestants = ArrayField(models.IntegerField(), blank=True)

    excluded_teams = models.ManyToManyField("users.Team", blank=True, related_name="+")

    def get_teams(self, ignore_excluded=False):
        qs = (
            Team.objects.filter(
                venue__category__competition=self.competition,
            )
            .select_related("venue", "venue__category", "school")
            .prefetch_related("contestants")
        )
        if not ignore_excluded:
            qs = qs.exclude(id__in=self.excluded_teams.all())

        if self.team_countries:
            qs = qs.filter(venue__country__in=self.team_countries)
        if self.team_languages:
            qs = qs.filter(language__in=self.team_languages)
        if self.team_venues.exists():
            qs = qs.filter(venue__in=self.team_venues.all())
        if self.team_statuses:
            qs = qs.has_status(self.team_statuses)
        if self.team_contestants:
            qs = qs.annotate(contestant_count=Count("contestants")).filter(
                contestant_count__in=self.team_contestants
            )

        return qs

    def send_single(self, team: Team, override_email=None):
        template = Template(self.template)

        with TeamCountry(team):
            branch = Branches[team.venue.category.competition.branch]
            link = country_reverse(
                "team_edit", kwargs={"secret_link": team.secret_link}
            )
            context = Context(
                {"team": team, "edit_link": f"https://{branch.domain}{link}"}
            )

            send_email(
                branch,
                override_email if override_email else team.contact_email,
                self.subject,
                "mail/messages/campaign.html",
                "mail/messages/campaign.txt",
                {"content": template.render(context)},
                [team.venue.contact_email],
            )

    def send_all(self):
        for team in self.get_teams():
            self.send_single(team)
