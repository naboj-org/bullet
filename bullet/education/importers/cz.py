import csv
from typing import Iterable

from education.importers.base import BaseSchoolImporter, ImportedSchool


class CzechSchoolImporter(BaseSchoolImporter):
    name = "cz"

    types = (
        (
            "zs",
            "Základní škola",
            "ZŠ (CZ)",
            (f"{i}. ročník" for i in range(1, 10)),
        ),
        (
            "ss",
            "Střední škola",
            "SŠ (CZ)",
            (f"{i}. ročník" for i in range(1, 5)),
        ),
        (
            "6gym",
            "Šestileté gymnázium",
            "6GYM (CZ)",
            (f"{i}. ročník" for i in range(1, 7)),
        ),
        (
            "8gym",
            "Osmileté gymnázium",
            "8GYM (CZ)",
            (
                "Prima",
                "Sekunda",
                "Tercie",
                "Kvarta",
                "Kvinta",
                "Sexta",
                "Septima",
                "Oktáva",
            ),
        ),
    )

    def get_schools(self) -> Iterable[ImportedSchool]:
        reader = csv.DictReader(self.file)

        for row in reader:
            types = []
            suffix = ""
            if row["Typ"][0] == "B":
                types.append("zs")
                suffix = "ZŠ"
            if row["Typ"][0] == "C":
                types.extend(["ss", "6gym", "8gym"])
                suffix = "SŠ"

            if types:
                address = f"{row['Ulice']}, {row['Místo']}"
                yield ImportedSchool(
                    f"{row['Zkrácený název']} ({suffix})",
                    address.strip(" ,"),
                    "CZ",
                    row["Plný název"],
                    types,
                    row["IZO"],
                )
