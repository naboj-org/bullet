import random

import factory
from bullet_admin.models import CompetitionRole, BranchRole
from django_countries import countries
from factory.django import DjangoModelFactory

from competitions.branches import Branches
from competitions.models import Competition, Venue
from users.models import User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        exclude = ("plaintext_password",)

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    password = factory.PostGenerationMethodCall("set_password", "defaultpassword")


class CompetitionRoleFactory(DjangoModelFactory):
    class Meta:
        model = CompetitionRole
        django_get_or_create = ["competition", "user"]

    competition = factory.Faker("random_element", elements=Competition.objects.all())
    countries = factory.Faker("random_elements", elements=countries)
    can_delegate = factory.Faker("boolean")
    is_operator = factory.Faker("boolean")
    user = factory.Faker("random_element", elements=User.objects.all())

    @factory.post_generation
    def post(self, create, extracted, **kwargs):
        venues = list(Venue.objects.all())
        self.venue_objects.set(random.sample(venues, random.randint(0, len(venues))))


class BranchRoleFactory(DjangoModelFactory):
    class Meta:
        model = BranchRole
        django_get_or_create = ["user", "branch"]

    is_translator = factory.Faker("boolean")
    is_admin = factory.Faker("boolean")
    branch = factory.Faker("random_element", elements=[b.id for b in Branches])
    user = factory.Faker("random_element", elements=User.objects.all())
