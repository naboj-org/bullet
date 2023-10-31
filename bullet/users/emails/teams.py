from competitions.branches import Branches
from countries.logic import country
from django.utils import translation
from django.utils.translation import gettext as _
from django_rq import job
from users.models import Team

from bullet.utils.email import send_email


class TeamCountry:
    def __init__(self, team):
        self.team = team

    def __enter__(self):
        self.old_lang = translation.get_language()
        translation.activate(self.team.language)

        self.old_country = country.get_country()
        country.activate(self.team.venue.country.code.lower())

    def __exit__(self, exc_type, exc_val, exc_tb):
        translation.activate(self.old_lang)
        country.activate(self.old_country)


@job
def send_confirmation_email(team_id: int):
    team = Team.objects.get(id=team_id)
    with TeamCountry(team):
        send_email(
            Branches[team.venue.category.competition.branch],
            team.contact_email,
            _("Confirm your team registration"),
            "mail/messages/registration.html",
            "mail/messages/registration.txt",
            {"team": team},
            [team.venue.contact_email],
        )


@job
def send_to_competition_email(team_id: int):
    team = Team.objects.get(id=team_id)
    with TeamCountry(team):
        send_email(
            Branches[team.venue.category.competition.branch],
            team.contact_email,
            _("Team moved from waiting list"),
            "mail/messages/to_competition.html",
            "mail/messages/to_competition.txt",
            {"team": team},
            [team.venue.contact_email],
        )


@job
def send_deletion_email(team: Team):
    # We must use pickled Team here as the team don't exist in the database
    with TeamCountry(team):
        send_email(
            Branches[team.venue.category.competition.branch],
            team.contact_email,
            _("Your team has been deleted"),
            "mail/messages/team_delete.html",
            "mail/messages/team_delete.txt",
            {"team": team},
            [team.venue.contact_email],
        )
