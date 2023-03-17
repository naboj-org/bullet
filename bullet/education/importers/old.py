import csv
from typing import Iterable

from education.importers.base import BaseSchoolImporter, ImportedSchool


class OldSchoolImporter(BaseSchoolImporter):
    name = "old"

    types = (
        (
            "at-ahs",
            "Allgemeinbildende Höhere Schule",
            "(old) AHS (AT)",
            (f"{i}. Schulstufe" for i in range(5, 13)),
        ),
        (
            "at-bhs",
            "Berufsbildende höherbildende Schule",
            "(old) BHS (AT)",
            (f"{i}. Schulstufe" for i in range(9, 14)),
        ),
        (
            "de",
            "Deutsch Schule",
            "(old) DE",
            (f"{i}. Klasse" for i in range(1, 13)),
        ),
        (
            "gb-scotland",
            "Scotland school",
            "(old) scotland (GB)",
            (
                "First year",
                "Second year",
                "Third year",
                "Fourth year",
                "Fifth year",
                "Sixth year",
            ),
        ),
        (
            "gb-england",
            "England school",
            "(old) england (GB)",
            (f"Year {i}" for i in range(10, 14)),
        ),
        (
            "ee",
            "Eesti kool",
            "(old) EE",
            (f"{i}" for i in range(1, 13)),
        ),
        (
            "ir",
            "Iran",
            "(old) IR",
            (f"{i}" for i in range(7, 13)),
        ),
        (
            "ch",
            "Switzerland",
            "(old) CH",
            (f"{i}" for i in range(1, 5)),
        ),
    )

    def get_schools(self) -> Iterable[ImportedSchool]:
        reader = csv.DictReader(self.file)

        for row in reader:
            yield ImportedSchool(
                row["name"],
                row["address"],
                row["country"],
                "",
                [row["type"]],
                row["id"],
            )
