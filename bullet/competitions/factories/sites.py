import factory
from competitions.models import CategoryCompetition, CompetitionSite, Site
from factory.django import DjangoModelFactory
from web.factories.addresses import AddressFactory

from bullet.constants import Languages


class SiteFactory(DjangoModelFactory):
    class Meta:
        model = Site

    name = factory.Faker("sentence")
    short_name = factory.Faker("word")
    address = factory.SubFactory(AddressFactory)


class CompetitionSiteFactory(DjangoModelFactory):
    class Meta:
        model = CompetitionSite

    category_competition = factory.Faker(
        "random_element", elements=CategoryCompetition.objects.all()
    )
    site = factory.Faker("random_element", elements=Site.objects.all())
    capacity = factory.Faker("pyint")

    accepted_languages = factory.Faker("random_elements", elements=Languages.values)
    results_announced = factory.Faker("boolean")
    participants_hidden = factory.Faker("boolean")
    email_alias = factory.Faker("email")
