from competitions.models import Competition

from problems.factories.problems import CategoryProblemFactory, ProblemFactory
from problems.models import Problem


def create_problems(competition: Competition) -> list[Problem]:
    problems = ProblemFactory.create_batch(42, competition=competition)
    CategoryProblemFactory.create_batch(42)
    return problems
