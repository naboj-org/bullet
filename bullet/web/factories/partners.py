import factory
from competitions.branches import Branches
from factory.django import DjangoModelFactory
from web.models import Organizer, Partner


class PartnerFactory(DjangoModelFactory):
    class Meta:
        model = Partner

    branch = factory.Faker("random_element", elements=Branches.choices())
    name = factory.Faker("word")
    url = factory.Faker("url")
    image = factory.Faker("image")


class OrganizerFactory(DjangoModelFactory):
    class Meta:
        model = Organizer

    branch = factory.Faker("random_element", elements=Branches.choices())
    name = factory.Faker("word")
    url = factory.Faker("url")
    image = factory.Faker("image")
