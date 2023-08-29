import factory
from competitions.models import CategoryCompetition, Venue
from countries.models import BranchCountry
from django.conf import settings
from factory.django import DjangoModelFactory


class VenueFactory(DjangoModelFactory):
    class Meta:
        model = Venue
        django_get_or_create = ["category_competition", "shortcode"]

    name = factory.Faker("sentence")
    shortcode = factory.Faker("hexify", text="^^^^^")
    address = factory.Faker("address")
    country = factory.Faker(
        "random_element",
        elements=BranchCountry.objects.values_list("country", flat=True),
    )
    category_competition = factory.Faker(
        "random_element", elements=CategoryCompetition.objects.all()
    )
    capacity = factory.Faker("pyint")

    accepted_languages = factory.Faker(
        "random_elements", elements=[x[0] for x in settings.LANGUAGES]
    )
    results_announced = factory.Faker("boolean")
    participants_hidden = factory.Faker("boolean")
    email = factory.Faker("email")
