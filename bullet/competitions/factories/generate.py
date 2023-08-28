import random

from competitions.factories.competition import (
    CategoryCompetitionFactory,
    EndedCompetitionFactory,
    RegistrationInProgressCompetitionFactory,
)
from competitions.factories.venues import VenueFactory
from competitions.models import Competition
from users.factories.contestants import ContestantFactory, TeamFactory


def feed_competition(competition=None) -> None:
    """
    Helper function that feeds competition with data.
    """
    for _ in range(2):
        category_competition = CategoryCompetitionFactory(competition=competition)
        venues = VenueFactory.create_batch(
            50, category_competition=category_competition
        )

        for _ in range(200):
            team = TeamFactory(venue=random.choice(venues))
            ContestantFactory.create_batch(
                random.randint(0, team.venue.category_competition.max_members_per_team),
                team=team,
            )


def create_registration_in_progress_competition(branch=None) -> Competition:
    """
    Helper function to generate a full reg. in progress competition with everything.
    """
    competition = RegistrationInProgressCompetitionFactory(branch=branch)
    feed_competition(competition)

    return competition


def create_ended_competition(branch=None) -> Competition:
    """
    Helper function to generate a full competition which has ended with everything.
    """
    competition = EndedCompetitionFactory(branch=branch)
    feed_competition(competition)

    return competition
