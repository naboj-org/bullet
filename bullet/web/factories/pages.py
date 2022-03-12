import factory
from competitions.models import Competition
from factory.django import DjangoModelFactory
from web.models import Page

from bullet.constants import Languages


class PageFactory(DjangoModelFactory):
    class Meta:
        model = Page

    url = factory.Faker("slug")
    language = factory.Faker("random_element", elements=Languages.values)
    branch = factory.Faker("random_element", elements=Competition.Branch.choices)
    title = factory.Faker("sentence")
    content = factory.Faker("text")
