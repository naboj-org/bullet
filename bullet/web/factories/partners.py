import factory
from competitions.branches import Branches
from django.core.files.base import ContentFile
from factory.django import DjangoModelFactory, ImageField
from web.models import Organizer, Partner


class RandomImage(ImageField):
    def _make_content(self, params):
        data = self._make_data(params)
        content = ContentFile(data)
        filename = f"{params.get('filename')}.{params.get('format')}"
        return filename, content


class PartnerFactory(DjangoModelFactory):
    class Meta:
        model = Partner

    branch = factory.Faker(
        "random_element", elements=[x[0] for x in Branches.choices()]
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


class OrganizerFactory(DjangoModelFactory):
    class Meta:
        model = Organizer

    branch = factory.Faker(
        "random_element", elements=[x[0] for x in Branches.choices()]
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
