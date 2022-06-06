import factory
from competitions.branches import Branches
from django.conf import settings
from factory.django import DjangoModelFactory
from web.models import Page


class PageFactory(DjangoModelFactory):
    class Meta:
        model = Page

    url = factory.Faker("slug")
    language = factory.Faker(
        "random_element", elements=[x[0] for x in settings.LANGUAGES]
    )
    branch = factory.Faker("random_element", elements=Branches.choices())
    title = factory.Faker("sentence")
    content = factory.Faker("text")
