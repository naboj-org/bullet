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
    competition_venues = VenueFactory.create_batch(2000)

    for _ in range(200):
        team = TeamFactory(competition_venue=random.choice(competition_venues))
        ContestantFactory.create_batch(
            random.randint(
                0, team.competition_venue.category_competition.max_members_per_team
            ),
            team=team,
        )

    return competition
