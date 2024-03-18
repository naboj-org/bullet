import csv
from typing import Iterable

from education.importers.base import BaseSchoolImporter, ImportedSchool


class SerbianSchoolImporter(BaseSchoolImporter):
    name = "rs"

    types = (
        (
            "rs",
            "Serbian school",
            "RS",
            (f"{i}" for i in range(1, 5)),
        ),
    )

    def get_schools(self) -> Iterable[ImportedSchool]:
        reader = csv.DictReader(self.file)

        for row in reader:
            address = f"{row['улица']} {row['број']}, {row['насеље']}"
            address = address.strip(", ")

            yield ImportedSchool(
                row["назив школе"],
                address,
                "RS",
                "",
                ["rs"],
                None,
            )
