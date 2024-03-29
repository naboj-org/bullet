import factory
from competitions.branches import Branches
from django.conf import settings
from django_countries import countries
from factory.django import DjangoModelFactory
from mdgen import MarkdownPostProvider
from web.models import Page

factory.Faker.add_provider(provider=MarkdownPostProvider)


class PageFactory(DjangoModelFactory):
    class Meta:
        model = Page

    slug = factory.Faker("slug")
    language = factory.Faker(
        "random_element", elements=[x[0] for x in settings.LANGUAGES]
    )
    branch = factory.Faker("random_element", elements=Branches.choices())
    title = factory.Faker("sentence")
    content = factory.Faker("post", size="large")
    countries = factory.Faker(
        "random_elements",
        elements=[x.code for x in countries],
        unique=True,
    )
