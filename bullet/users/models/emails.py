from bullet.utils.email import send_email
from competitions.branches import Branches
from countries.utils import country_reverse
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Count, Min
from django.db.models.functions import Lower
from django.template import Context, Template
from django_countries.fields import CountryField
from django_rq import job
from web.fields import ChoiceArrayField, LanguageField

from users.emails.teams import TeamCountry
from users.models import Team, TeamStatus


@job
def _send_campaign(campaign_id: int, team_id: int, override_email=None):
    campaign = EmailCampaign.objects.get(id=campaign_id)
    team = Team.objects.get(id=team_id)
    template = Template(campaign.template)

    with TeamCountry(team):
        branch = Branches[team.venue.category.competition.branch]
        context = Context()
        if not campaign.unique_email_addresses:
            link = country_reverse(
                "team_edit", kwargs={"secret_link": team.secret_link}
            )
            context.update(
                {"team": team, "edit_link": f"https://{branch.domain}{link}"}
            )

        send_email(
            branch,
            override_email if override_email else team.contact_email,
            campaign.subject,
            "mail/messages/campaign.html",
            "mail/messages/campaign.txt",
            {"content": template.render(context)},
            [team.venue.contact_email],
        )


class EmailCampaign(models.Model):
    competition = models.ForeignKey(
        "competitions.Competition", on_delete=models.CASCADE
    )
    subject = models.CharField(max_length=128)
    template = models.TextField(blank=True)
    unique_email_addresses = models.BooleanField(default=False)
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

    class Meta:
        ordering = ["-last_sent", "subject"]

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
        _send_campaign.delay(self.id, team.id, override_email=override_email)

    def get_recipient_teams(self):
        teams = self.get_teams()
        if not self.unique_email_addresses:
            return teams

        # Apply selection filters separately so contestant counts do not
        # change the grouping used to choose one team per email address.
        recipient_ids = (
            Team.objects.filter(pk__in=teams.values("pk"))
            .order_by()
            .values(normalized_email=Lower("contact_email"))
            .annotate(recipient_id=Min("pk"))
            .values("recipient_id")
        )
        return teams.filter(pk__in=recipient_ids).order_by("pk")

    def get_recipient_count(self):
        return self.get_recipient_teams().count()

    def send_all(self):
        for team in self.get_recipient_teams():
            self.send_single(team)
