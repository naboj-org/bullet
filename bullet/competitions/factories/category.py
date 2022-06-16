import factory
from competitions.branches import Branches
from competitions.models import Category, CategoryDescription
from django.conf import settings
from django_countries import countries
from factory.django import DjangoModelFactory


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    branch = factory.Faker("random_element", elements=Branches.choices())
    name = factory.Faker("word")
    slug = factory.Faker("word")


class CategoryDescriptionFactory(DjangoModelFactory):
    class Meta:
        model = CategoryDescription

    category = factory.Faker("random_element", elements=Category.objects.all())
    name = factory.Faker("word")
    description = factory.Faker("paragraph")
    language = factory.Faker(
        "random_element", elements=[x[0] for x in settings.LANGUAGES]
    )
    countries = factory.Faker(
        "random_elements", elements=[x.code for x in countries], unique=True
    )
