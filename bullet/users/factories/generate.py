from competitions.models import Competition
from users.factories.user import CompetitionRoleFactory, UserFactory, BranchRoleFactory


def create_users(competition: "Competition"):
    UserFactory.create_batch(10)
    CompetitionRoleFactory.create_batch(10)
    BranchRoleFactory.create_batch(10)
