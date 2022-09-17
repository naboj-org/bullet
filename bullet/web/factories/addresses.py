import factory
from address.models import Address, Country, Locality, State
from factory.django import DjangoModelFactory


class CountryFactory(DjangoModelFactory):
    class Meta:
        model = Country
        django_get_or_create = ["name"]

    name = factory.Faker("word")
    code = factory.Faker("country_code")


class StateFactory(DjangoModelFactory):
    class Meta:
        model = State
        django_get_or_create = ["code"]

    name = factory.Faker("word")
    code = factory.Faker("lexify", text="????")
    country = factory.SubFactory(CountryFactory)


class LocalityFactory(DjangoModelFactory):
    class Meta:
        model = Locality
        django_get_or_create = ["postal_code"]

    name = factory.Faker("city")
    postal_code = factory.Faker("postcode")
    state = factory.SubFactory(StateFactory)


class AddressFactory(DjangoModelFactory):
    class Meta:
        model = Address

    street_number = factory.Faker("building_number")
    route = factory.Faker("street_name")
    # locality = factory.SubFactory(LocalityFactory)
    raw = factory.Faker("address")
    latitude = factory.Faker("latitude")
    longitude = factory.Faker("longitude")
