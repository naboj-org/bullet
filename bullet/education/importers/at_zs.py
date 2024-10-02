import csv
from typing import Iterable

from education.importers.base import BaseSchoolImporter, ImportedSchool


class AustrianPrimarySchoolImporter(BaseSchoolImporter):
    name = "at_zs"

    types = (
        (
            "ms",
            "Mittelschule",
            "AT",
            (f"{i}. Schulstufe" for i in range(5, 9)),
        ),
    )

    def get_schools(self) -> Iterable[ImportedSchool]:
        reader = csv.DictReader(self.file)

        for row in reader:
            yield ImportedSchool(
                row["Titel"],
                row["Adresse"],
                "AT",
                "",
                ["ms"],
                row["Schulkennzahl"],
            )
