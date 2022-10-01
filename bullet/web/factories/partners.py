import factory
from competitions.branches import Branches
from django.core.files.base import ContentFile
from django_countries import countries
from factory.django import DjangoModelFactory, ImageField
from web.models import Logo


class RandomImage(ImageField):
    def _make_content(self, params):
        data = self._make_data(params)
        content = ContentFile(data)
        filename = f"{params.get('filename')}.{params.get('format')}"
        return filename, content


class LogoFactory(DjangoModelFactory):
    class Meta:
        model = Logo

    branch = factory.Faker(
        "random_element", elements=[x[0] for x in Branches.choices()]
    )
    type = factory.Faker("random_element", elements=Logo.Type.values)
    countries = factory.Faker(
        "random_elements",
        elements=[x.code for x in countries],
        unique=True,
    )
    name = factory.Faker("word")
    url = factory.Faker("url")
    image = RandomImage(
        color=factory.Faker("color"),
        format=factory.Faker("random_element", elements=["jpeg", "png", "bmp", "gif"]),
        height=factory.Faker("random_number", digits=3, fix_len=True),
        width=factory.Faker("random_number", digits=3, fix_len=True),
        filename=factory.SelfAttribute("..name"),
    )
