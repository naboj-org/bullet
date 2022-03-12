import factory
from education.models import Education, Grade, SchoolType
from factory.django import DjangoModelFactory


class EducationFactory(DjangoModelFactory):
    class Meta:
        model = Education

    name = factory.Faker("word")

    @factory.post_generation
    def grades(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        self.grades.add(*extracted)


class GradeFactory(DjangoModelFactory):
    class Meta:
        model = Grade

    school_type = factory.Faker("random_element", elements=SchoolType.objects.all())
    name = factory.Faker("word")
    order = factory.Sequence(lambda x: x)
