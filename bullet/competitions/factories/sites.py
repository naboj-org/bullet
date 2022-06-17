import factory
from competitions.models import CategoryCompetition, CompetitionVenue, Venue
from django.conf import settings
from factory.django import DjangoModelFactory
from web.factories.addresses import AddressFactory


class VenueFactory(DjangoModelFactory):
    class Meta:
        model = Venue

    name = factory.Faker("sentence")
    short_name = factory.Faker("word")
    address = factory.SubFactory(AddressFactory)


class CompetitionVenueFactory(DjangoModelFactory):
    class Meta:
        model = CompetitionVenue
        django_get_or_create = ["category_competition", "venue"]

    category_competition = factory.Faker(
        "random_element", elements=CategoryCompetition.objects.all()
    )
    venue = factory.Faker("random_element", elements=Venue.objects.all())
    capacity = factory.Faker("pyint")

    accepted_languages = factory.Faker(
        "random_elements", elements=[x[0] for x in settings.LANGUAGES]
    )
    results_announced = factory.Faker("boolean")
    participants_hidden = factory.Faker("boolean")
    email_alias = factory.Faker("email")
