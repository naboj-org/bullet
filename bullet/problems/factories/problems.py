import factory
from competitions.models import Competition
from factory.django import DjangoModelFactory

from problems.models import Problem


class ProblemFactory(DjangoModelFactory):
    class Meta:
        model = Problem

    number = factory.Faker("random_int")
    competition = factory.Faker("random_element", elements=Competition.objects.all())
