import csv
from typing import Iterable

from education.importers.base import BaseSchoolImporter, ImportedSchool


class BelgianSchoolImporter(BaseSchoolImporter):
    name = "be"

    types = (
        (
            "so",
            "SO",
            "BE",
            (f"klas {i}" for i in range(1, 7)),
        ),
    )

    def get_schools(self) -> Iterable[ImportedSchool]:
        reader = csv.DictReader(self.file, delimiter=";")

        for row in reader:
            yield ImportedSchool(
                row["naam"],
                row["adres"],
                "BE",
                "",
                ["so"],
                f"{row['schoolnummer']}/{row['intern_vplnummer']}",
            )
