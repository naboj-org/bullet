import csv
from typing import Iterable

from education.importers.base import BaseSchoolImporter, ImportedSchool


class CroatianSchoolImporter(BaseSchoolImporter):
    name = "hr"

    types = (
        (
            "os",
            "Osnovna škola",
            "HR",
            (f"{i}. razred" for i in range(1, 9)),
        ),
    )

    def get_schools(self) -> Iterable[ImportedSchool]:
        reader = csv.DictReader(self.file)

        for row in reader:
            address = f"{row['Adresa']}, {row['Mjesto']}"

            yield ImportedSchool(
                row["Naziv"],
                address.strip(" ,"),
                "HR",
                "",
                ["os"],
                row["Šifra"],
            )
