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
    for _ in range(2):
        category_competition = CategoryCompetitionFactory(competition=competition)
        venues = VenueFactory.create_batch(50, category_competition=category_competition)

        for _ in range(200):
            team = TeamFactory(venue=random.choice(venues))
            ContestantFactory.create_batch(
                random.randint(0, team.venue.category_competition.max_members_per_team),
                team=team,
            )

    return competition
