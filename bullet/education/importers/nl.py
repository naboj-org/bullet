import csv
from typing import Iterable

from education.importers.base import BaseSchoolImporter, ImportedSchool


class DutchSchoolImporter(BaseSchoolImporter):
    name = "nl"

    types = (
        (
            "nl",
            "HAVO/VWO",
            "NL",
            (f"klas {i}" for i in range(1, 7)),
        ),
    )

    def get_schools(self) -> Iterable[ImportedSchool]:
        reader = csv.DictReader(self.file)

        for row in reader:
            yield ImportedSchool(
                row["School Name"],
                "",
                "NL",
                "",
                ["nl"],
                None,
            )
