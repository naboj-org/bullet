import factory
from competitions.models import CategoryCompetition, Competition
from factory.django import DjangoModelFactory
from problems.models import CategoryProblem, Problem


class ProblemFactory(DjangoModelFactory):
    class Meta:
        model = Problem

    name = factory.Faker("sentence")
    competition = factory.Faker("random_element", elements=Competition.objects.all())


class CategoryProblemFactory(DjangoModelFactory):
    class Meta:
        model = CategoryProblem
        django_get_or_create = ("problem", "category", "number")

    problem = factory.Faker("random_element", elements=Problem.objects.all())
    category = factory.Faker(
        "random_element", elements=CategoryCompetition.objects.all()
    )
    number = factory.Faker("random_int")
