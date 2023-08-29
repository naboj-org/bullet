import random

import factory
from competitions.branches import Branches
from countries.models import BranchCountry
from django.conf import settings
from django_countries import countries
from factory.django import DjangoModelFactory


class BranchCountryFactory(DjangoModelFactory):
    class Meta:
        model = BranchCountry

    branch = factory.Faker(
        "random_element", elements=[x[0] for x in Branches.choices()]
    )
    country = factory.Iterator(
        [x for x in random.sample(sorted(countries), len(countries)) if x[0] != "SK"],
        cycle=False,
    )
    languages = factory.Faker(
        "random_elements",
        elements=[x[0] for x in settings.LANGUAGES],
        unique=True,
        length=random.randint(1, 4),
    )
    timezone = factory.Faker("timezone")
    email = factory.Faker("email")
