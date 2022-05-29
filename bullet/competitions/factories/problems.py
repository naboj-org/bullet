import factory
from competitions.models import (
    CategoryCompetition,
    CompetitionProblem,
    LocalizedProblem,
    Problem,
    SolutionSubmitLog,
)
from factory.django import DjangoModelFactory
from users.models import Team, User

from bullet.constants import Languages


class ProblemFactory(DjangoModelFactory):
    class Meta:
        model = Problem

    name = factory.Faker("sentence")


class LocalizedProblemFactory(DjangoModelFactory):
    class Meta:
        model = LocalizedProblem

    problem = factory.Faker("random_element", elements=Problem.objects.all())
    language = factory.Faker("random_element", elements=Languages.values)
    statement_text = factory.Faker("paragraph")
    result_text = factory.Faker("sentence")
    solution_text = factory.Faker("paragraph")


class CompetitionProblemFactory(DjangoModelFactory):
    class Meta:
        model = CompetitionProblem

    category_competition = factory.Faker(
        "random_element", elements=CategoryCompetition.objects.all()
    )
    problem = factory.Faker("random_element", elements=Problem.objects.all())
    number = factory.Sequence(lambda n: n)


class SolutionSubmitLogFactory(DjangoModelFactory):
    class Meta:
        model = SolutionSubmitLog

    # TODO: Might generate submits from teams
    #  that are not participating for this competition
    problem = factory.Faker("random_element", elements=Problem.objects.all())
    team = factory.Faker("random_element", elements=Team.objects.all())
    staff = factory.Faker("random_element", elements=User.objects.all())
    submitted_at = factory.Faker("datetime")
