import factory
from competitions.models import Venue
from django.conf import settings
from django.utils import timezone
from education.models import Grade, School
from factory.django import DjangoModelFactory
from users.models import Contestant, Team


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

    registered_at = factory.Faker(
        "past_datetime", tzinfo=timezone.get_current_timezone()
    )
    confirmed_at = factory.Faker(
        "past_datetime", tzinfo=timezone.get_current_timezone()
    )

    venue = factory.Faker("random_element", elements=Venue.objects.all())
    number = factory.Sequence(lambda n: n)
    in_school_symbol = factory.Faker("random_letter")

    is_reviewed = factory.Faker("boolean")


class ContestantFactory(DjangoModelFactory):
    class Meta:
        model = Contestant

    team = factory.Faker("random_element", elements=Team.objects.all())

    full_name = factory.Faker("name")
    grade = factory.Faker("random_element", elements=Grade.objects.all())
