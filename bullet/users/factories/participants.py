import factory
from competitions.models import CompetitionSite
from factory.django import DjangoModelFactory
from users.models import Participant, School, Team
from web.factories.addresses import AddressFactory

from bullet.constants import Languages


class SchoolFactory(DjangoModelFactory):
    class Meta:
        model = School

    name = factory.Faker("sentence")
    type = factory.Faker("random_element", elements=School.SchoolType.values)

    address = factory.SubFactory(AddressFactory)
    izo = factory.Faker("lexify", text="???? ???")


class TeamFactory(DjangoModelFactory):
    class Meta:
        model = Team
        django_get_or_create = ["school", "in_school_symbol"]

    contact_name = factory.Faker("name")
    contact_email = factory.Faker("email")
    contact_phone = factory.Faker("phone_number")
    secret_link = factory.Faker("hexify", text="^" * 48)

    school = factory.Faker("random_element", elements=School.objects.all())
    language = factory.Faker("random_element", elements=Languages.values)

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

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    graduation_year = factory.Faker("year")
    birth_year = factory.Faker("year")
