# Note to future readers: this file is intentionally named `competition.py` despite
# the model file being called `competitions` to avoid import problems.
import datetime
import random

import factory
import faker
from competitions.branches import Branches
from competitions.models import CategoryCompetition, Competition
from django.utils import timezone
from education.models import Education, School
from factory.django import DjangoModelFactory

fake = faker.Faker()


def make_date_after(date):
    return fake.date_time_between(
        start_date=date,
        end_date=date + datetime.timedelta(days=30),
        tzinfo=timezone.get_current_timezone(),
    )


def make_duration():
    return datetime.timedelta(minutes=fake.random.randint(15, 240))


class CompetitionFactory(DjangoModelFactory):
    class Meta:
        model = Competition

    name = factory.Faker("sentence")
    branch = factory.Faker("random_element", elements=[b.id for b in Branches])
    number = factory.Faker("pyint")

    web_start = factory.Faker("date_time", tzinfo=timezone.get_current_timezone())
    registration_start = factory.Faker(
        "date_time_between", tzinfo=timezone.get_current_timezone()
    )
    # TODO: maybe allow this to be None
    registration_second_round_start = factory.LazyAttribute(
        lambda o: make_date_after(o.registration_start)
    )
    registration_end = factory.Faker(
        "future_datetime",
        tzinfo=timezone.get_current_timezone(),
    )

    competition_start = factory.LazyAttribute(
        lambda o: make_date_after(o.registration_end)
    )
    competition_duration = factory.LazyAttribute(lambda o: make_duration())

    is_cancelled = factory.Faker("boolean", chance_of_getting_true=10)


class CategoryCompetitionFactory(DjangoModelFactory):
    class Meta:
        model = CategoryCompetition
        django_get_or_create = ["competition", "identifier"]

    competition = factory.Faker("random_element", elements=Competition.objects.all())
    identifier = factory.Faker("slug")
    order = factory.Faker("pyint")

    @factory.post_generation
    def educations(self, create, extracted, **kwargs):
        if not create:
            return

        if not extracted:
            extracted = []
            for e in Education.objects.all():
                if random.randint(0, 1):
                    extracted.append(e)

        self.educations.add(*extracted)

    problems_per_team = factory.Faker("pyint", min_value=1, max_value=60)
    max_teams_per_school = factory.Faker("pyint", max_value=100)
    max_teams_second_round = factory.Faker("pyint", max_value=100)
    max_members_per_team = factory.Faker("pyint", min_value=1, max_value=10)


class WildcardFactory(DjangoModelFactory):
    competition = factory.Faker("random_element", elements=Competition.objects.all())
    school = factory.Faker("random_element", elements=School.objects.all())
    note = factory.Faker("sentence")
