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
        (
            "ss",
            "Srednja škola",
            "HR",
            (f"{i}. razred" for i in range(1, 5)),
        ),
    )

    type_map = {
        "Osnovna škola": "os",
        "Srednja škola": "ss",
    }

    def get_schools(self) -> Iterable[ImportedSchool]:
        reader = csv.DictReader(self.file)

        for row in reader:
            address = f"{row['Adresa']}, {row['Mjesto']}"

            types = [x.strip() for x in row["TipUstanove"].split(",")]

            our_types = []
            for type_ in types:
                if type_ not in self.type_map:
                    continue
                our_types.append(self.type_map[type_])

            yield ImportedSchool(
                row["Naziv"],
                address.strip(" ,"),
                "HR",
                "",
                our_types,
                row["Šifra"],
            )
