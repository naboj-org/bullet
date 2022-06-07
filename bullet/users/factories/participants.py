import factory
from competitions.models import CompetitionSite
from django.conf import settings
from education.models import School
from factory.django import DjangoModelFactory
from users.models import Participant, Team


class TeamFactory(DjangoModelFactory):
    class Meta:
        model = Team
        django_get_or_create = ["school", "in_school_symbol"]

    contact_name = factory.Faker("name")
    contact_email = factory.Faker("email")
    contact_phone = factory.Faker("phone_number")
    secret_link = factory.Faker("hexify", text="^" * 48)

    school = factory.Faker("random_element", elements=School.objects.all())
    language = factory.Faker(
        "random_element", elements=[x[0] for x in settings.LANGUAGES]
    )

    registered_at = factory.Faker("past_datetime")
    confirmed_at = factory.Faker("past_datetime")
    approved_at = factory.Faker("past_datetime")

    competition_site = factory.Faker(
        "random_element", elements=CompetitionSite.objects.all()
    )
    number = factory.Sequence(lambda n: n)
    in_school_symbol = factory.Faker("random_letter")

    is_official = factory.Faker("boolean")
    is_reviewed = factory.Faker("boolean")


class ParticipantFactory(DjangoModelFactory):
    class Meta:
        model = Participant

    team = factory.Faker("random_element", elements=Team.objects.all())

    full_name = factory.Faker("name")
    graduation_year = factory.Faker("year")
    birth_year = factory.Faker("year")
