import random

from competitions.factories.category import CategoryDescriptionFactory, CategoryFactory
from competitions.factories.competition import (
    CategoryCompetitionFactory,
    CompetitionFactory,
)
from competitions.factories.sites import CompetitionSiteFactory, SiteFactory
from competitions.models import Competition
from users.factories.participants import ParticipantFactory, TeamFactory


def create_base():
    """
    Helper function to generate common data
    """
    SiteFactory.create_batch(20)


def create_competition(branch=None) -> Competition:
    """
    Helper function to generate a full competition with everything.
    """
    competition = CompetitionFactory(branch=branch)
    CategoryFactory.create_batch(3, branch=branch)
    CategoryDescriptionFactory.create_batch(5)
    CategoryCompetitionFactory.create_batch(2, competition=competition)
    competition_sites = CompetitionSiteFactory.create_batch(5)

    for _ in range(200):
        team = TeamFactory(competition_site=random.choice(competition_sites))
        ParticipantFactory.create_batch(
            random.randint(
                0, team.competition_site.category_competition.max_members_per_team
            ),
            team=team,
        )

    return competition
