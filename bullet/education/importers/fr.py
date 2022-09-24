import csv
from typing import Iterable

from education.importers.base import BaseSchoolImporter, ImportedSchool


class FrenchSchoolImporter(BaseSchoolImporter):
    name = "es"

    types = (
        (
            "college",
            "Collège",
            "FR",
            ("Sixième", "Cinquième", "Quatrième", "Troisième"),
        ),
    )

    def get_schools(self) -> Iterable[ImportedSchool]:
        reader = csv.DictReader(self.file)

        for row in reader:
            yield ImportedSchool(
                row["name"],
                row["address"].strip(" -"),
                "FR",
                "",
                ["college"],
                None,
            )
