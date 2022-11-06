from dataclasses import dataclass

from bullet_admin.utils import get_venue_admin_emails
from competitions.branches import Branches
from competitions.models import Venue

from bullet.utils.email import send_email


@dataclass
class UnregisteredTeam:
    id: str
    code: str
    venue: Venue
    name: str
    contestants: str


def send_team_unregistered(team: UnregisteredTeam):
    send_email(
        Branches[team.venue.category_competition.competition.branch],
        get_venue_admin_emails(team.venue),
        "A team has been unregistered",
        "mail/messages/team_unregister.html",
        "mail/messages/team_unregister.txt",
        {"team": team},
    )
