import csv
from typing import Iterable

from education.importers.base import BaseSchoolImporter, ImportedSchool


class WalesSchoolImporter(BaseSchoolImporter):
    name = "wales"

    types = (
        (
            "wales",
            "Wales school",
            "(old) england (Wales)",
            (f"Year {i}" for i in range(10, 14)),
        ),
    )

    def get_schools(self) -> Iterable[ImportedSchool]:
        reader = csv.reader(self.file)

        for row in reader:
            yield ImportedSchool(
                row[1],
                row[2],
                "GB",
                "",
                ["wales"],
                row[0],
            )
