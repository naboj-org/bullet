# Note to future readers: this file is intentionally named `competition.py` despite
# the model file being called `competitions` to avoid import problems.
import datetime

import factory
import faker
from competitions.branches import Branches
from competitions.models import Category, CategoryCompetition, Competition
from education.models import School
from factory.django import DjangoModelFactory

fake = faker.Faker()


def make_date_after(date):
    return fake.date_between(start_date=date)


def make_duration():
    return datetime.timedelta(minutes=fake.random.randint(15, 240))


class CompetitionFactory(DjangoModelFactory):
    class Meta:
        model = Competition

    name = factory.Faker("sentence")
    branch = factory.Faker("random_element", elements=[b.id for b in Branches])

    graduation_year = factory.Faker("year")

    web_start = factory.Faker("date_time")
    registration_start = factory.Faker("date_between")
    # TODO: maybe allow this to be None
    registration_second_round_start = factory.LazyAttribute(
        lambda o: make_date_after(o.registration_start)
    )
    registration_end = factory.LazyAttribute(
        lambda o: make_date_after(o.registration_start)
    )

    competition_start = factory.LazyAttribute(
        lambda o: make_date_after(o.registration_end)
    )
    competition_duration = factory.LazyAttribute(lambda o: make_duration())

    is_cancelled = factory.Faker("boolean", chance_of_getting_true=10)


class CategoryCompetitionFactory(DjangoModelFactory):
    class Meta:
        model = CategoryCompetition
        django_get_or_create = ["competition", "category"]

    competition = factory.Faker("random_element", elements=Competition.objects.all())
    category = factory.Faker("random_element", elements=Category.objects.all())

    problems_per_team = factory.Faker("pyint", min_value=1, max_value=60)
    max_teams_per_school = factory.Faker("pyint", max_value=100)
    max_teams_second_round = factory.Faker("pyint", max_value=100)
    max_members_per_team = factory.Faker("pyint", min_value=1, max_value=10)

    ranking = factory.Faker(
        "random_elements", elements=CategoryCompetition.RankingCriteria.values
    )


class WildcardFactory(DjangoModelFactory):
    competition = factory.Faker("random_element", elements=Competition.objects.all())
    school = factory.Faker("random_element", elements=School.objects.all())
    note = factory.Faker("sentence")
