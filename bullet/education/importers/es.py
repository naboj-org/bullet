import csv
from typing import Iterable

from education.importers.base import BaseSchoolImporter, ImportedSchool


class SpanishSchoolImporter(BaseSchoolImporter):
    name = "es"

    types = (
        (
            "es",
            "School",
            "ES",
            (f"{i}. grade" for i in range(1, 10)),
        ),
    )

    def get_schools(self) -> Iterable[ImportedSchool]:
        reader = csv.DictReader(self.file)
        types = []

        for row in reader:
            address = f"{row['Address']}, {row['City/Town']}"
            types.append("es")

            yield ImportedSchool(
                row["Name of the School"],
                address.strip(" ,"),
                "ES",
                "",
                types,
                row["School Id."],
            )
