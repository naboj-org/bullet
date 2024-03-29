import random

import factory
from django_countries import countries
from education.models import School, SchoolType
from factory.django import DjangoModelFactory


class SchoolTypeFactory(DjangoModelFactory):
    class Meta:
        model = SchoolType

    name = factory.Faker("word")
    note = factory.Faker("word")


class SchoolFactory(DjangoModelFactory):
    class Meta:
        model = School

    name = factory.Faker("sentence")
    address = factory.Faker("address")
    country = factory.Faker("random_element", elements=[x.code for x in countries])

    @factory.post_generation
    def types(self, create, extracted, **kwargs):
        if not create:
            return

        if not extracted:
            extracted = []
            for e in SchoolType.objects.all():
                if random.randint(0, 1):
                    extracted.append(e)

        self.types.add(*extracted)
