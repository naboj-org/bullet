import csv
from typing import Iterable

from education.importers.base import BaseSchoolImporter, ImportedSchool


class HungarianSchoolImporter(BaseSchoolImporter):
    name = "hu"

    types = (
        (
            "gim",
            "gimnázium",
            "HU",
            (str(i) for i in range(5, 13)),
        ),
        (
            "szakgim",
            "szakgimnázium",
            "HU",
            (str(i) for i in range(9, 13)),
        ),
        (
            "szakkozeskola",
            "szakközépiskola",
            "HU",
            (str(i) for i in range(9, 12)),
        ),
        (
            "szakskola",
            "szakiskola",
            "HU",
            (str(i) for i in range(9, 11)),
        ),
    )

    type_mapping = {
        "gimnáziumi nevelés-oktatás": "gim",
        "szakgimnáziumi nevelés-oktatás": "szakgim",
        "szakközépiskolai nevelés-oktatás": "szakkozeskola",
        "szakiskolai nevelés-oktatás": "szakskola",
    }

    def get_schools(self) -> Iterable[ImportedSchool]:
        reader = csv.DictReader(self.file)

        school: ImportedSchool | None = None

        for row in reader:
            if school and school.identifier != row["OM azonosító"]:
                yield school
                school = None

            types = set()
            for col, typ in self.type_mapping.items():
                if row[col] == "X":
                    types.add(typ)

            if not types:
                continue

            if not school:
                address = f"{row['Intézmény cím']}, {row['Intézmény helység']}"
                school = ImportedSchool(
                    row["Intézmény neve"],
                    address.strip(", "),
                    "HU",
                    "",
                    list(types),
                    row["OM azonosító"],
                )
            else:
                school.types = list(set(school.types) | types)

        if school:
            yield school
