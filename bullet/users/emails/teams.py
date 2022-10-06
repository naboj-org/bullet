from competitions.branches import Branches
from countries.logic import country
from django.utils import translation
from django.utils.translation import gettext as _
from users.models import Team

from bullet.utils.email import send_email


def send_confirmation_email(team: Team):
    lang = translation.get_language()
    translation.activate(team.language)

    c = country.get_country()
    country.activate(team.venue.country.code.lower())

    send_email(
        Branches[team.venue.category_competition.competition.branch],
        team.contact_email,
        _("Confirm your team registration"),
        "mail/messages/registration.html",
        "mail/messages/registration.txt",
        {"team": team},
        [team.venue.contact_email],
    )

    # rollback global changes
    translation.activate(lang)
    country.activate(c)
