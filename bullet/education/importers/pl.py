import csv
from typing import Iterable

from education.importers.base import BaseSchoolImporter, ImportedSchool


class PolishSchoolImporter(BaseSchoolImporter):
    name = "pl"

    types = (
        (
            "sp",
            "Szkoła podstawowa",
            "PL",
            (f"Klasa {i}" for i in range(1, 9)),
        ),
        (
            "technikum",
            "Technikum",
            "PL",
            (f"Klasa {i}" for i in range(1, 6)),
        ),
        (
            "liceum",
            "Liceum",
            "PL",
            (f"Klasa {i}" for i in range(1, 5)),
        ),
    )

    type_mapping = {
        "Szkoła podstawowa": "sp",
        "Technikum": "technikum",
        "Liceum sztuk plastycznych": "liceum",
        "Liceum ogólnokształcące": "liceum",
    }

    def _parse_eq(self, x: str) -> str:
        if x[0] != "=":
            return x
        return x[2:-1]

    def get_schools(self) -> Iterable[ImportedSchool]:
        reader = csv.DictReader(self.file, delimiter=";")

        for row in reader:
            number = self._parse_eq(row["Numer budynku"])
            address = f"{row['Ulica']} {number}, {row['Miejscowość']}"

            if row["Typ"] not in self.type_mapping:
                continue

            yield ImportedSchool(
                row["Nazwa"],
                address.strip(", "),
                "PL",
                "",
                [self.type_mapping[row["Typ"]]],
                row[reader.fieldnames[0]],
            )
