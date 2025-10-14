import random

import factory
from bullet_admin.models import BranchRole, CompetitionRole
from competitions.branches import Branches
from competitions.models import Competition, Venue
from django_countries import countries as django_countries
from factory.django import DjangoModelFactory
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
    user = factory.Faker("random_element", elements=User.objects.all())

    @factory.post_generation
    def post(self, create, extracted, **kwargs):
        venues = list(Venue.objects.all())
        seed = ord(self.user.email[0].upper()) - ord("A")
        random.seed(seed)
        self.is_operator = random.random() > 0.5
        if random.random() > 0.5:
            self.venue_objects.set(
                random.sample(venues, random.randint(0, len(venues)))
            )
        else:
            self.countries = list(
                random.sample(
                    [x[0] for x in django_countries],
                    random.randint(0, len(django_countries)),
                )
            )


class BranchRoleFactory(DjangoModelFactory):
    class Meta:
        model = BranchRole
        django_get_or_create = ["user", "branch"]

    is_admin = factory.Faker("boolean")
    branch = factory.Faker("random_element", elements=[b.id for b in Branches])
    user = factory.Faker("random_element", elements=User.objects.all())
