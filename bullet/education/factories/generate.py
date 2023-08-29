from education.factories.educations import EducationFactory, GradeFactory
from education.factories.schools import SchoolFactory, SchoolTypeFactory


def create_education():
    school_types = [
        ("ZŠ", range(1, 10)),
        ("4GYM", range(1, 5)),
        ("8GYM", range(1, 9)),
    ]

    for st in school_types:
        school_type = SchoolTypeFactory(name=st[0])

        grades = []
        for i in st[1]:
            grades.append(
                GradeFactory(order=i, school_type=school_type, name=f"Year {i}")
            )

        EducationFactory(grades=grades)

    SchoolFactory.create_batch(100)
