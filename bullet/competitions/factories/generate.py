import random

from competitions.factories.competition import (
    CategoryCompetitionFactory,
    CompetitionFactory,
)
from competitions.factories.venues import VenueFactory
from competitions.models import Competition
from users.factories.contestants import ContestantFactory, TeamFactory


def create_competition(branch=None) -> Competition:
    """
    Helper function to generate a full competition with everything.
    """
    competition = CompetitionFactory(branch=branch)
    CategoryCompetitionFactory.create_batch(2, competition=competition)
    venues = VenueFactory.create_batch(50)

    for _ in range(200):
        team = TeamFactory(venue=random.choice(venues))
        ContestantFactory.create_batch(
            random.randint(0, team.venue.category_competition.max_members_per_team),
            team=team,
        )

    return competition
