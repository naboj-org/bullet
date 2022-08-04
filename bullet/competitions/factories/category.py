import factory
from competitions.branches import Branches
from competitions.models import Category
from factory.django import DjangoModelFactory


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    branch = factory.Faker("random_element", elements=Branches.choices())
    name = factory.Faker("word")
    slug = factory.Faker("word")
