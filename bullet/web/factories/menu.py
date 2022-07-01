import factory
from competitions.branches import Branches
from django.conf import settings
from django_countries import countries
from factory.django import DjangoModelFactory
from web.models import Menu


class MenuFactory(DjangoModelFactory):
    class Meta:
        model = Menu

    url = factory.Faker("slug")
    branch = factory.Faker("random_element", elements=Branches.choices())
    language = factory.Faker("random_element", elements=settings.LANGUAGES)
    countries = factory.Faker(
        "random_elements",
        elements=[x.code for x in countries],
        unique=True,
    )
    title = factory.Faker("word")
    order = factory.Faker("random_number")
    is_external = False

    class Params:
        external = factory.Trait(is_external=True, url=factory.Faker("url"))
