import csv
from typing import Iterable

from education.importers.base import BaseSchoolImporter, ImportedSchool


class RomanianSchoolImporter(BaseSchoolImporter):
    name = "old_ro"

    types = (
        (
            "old_ro",
            "şcoală",
            "(old) romania",
            (f"{i}" for i in range(1, 13)),
        ),
    )

    def get_schools(self) -> Iterable[ImportedSchool]:
        reader = csv.reader(self.file)

        for row in reader:
            yield ImportedSchool(
                row[1],
                row[2],
                "RO",
                "",
                ["old_ro"],
                row[0],
            )
