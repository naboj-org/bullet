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
        reader = sorted(reader, key=lambda x: x["Kód RÚIAN"])

        school = None
        ruian = None
        for row in reader:
            if school and ruian != row["Kód RÚIAN"]:
                if school.types:
                    yield school
                school = None
                ruian = None

            if school is None:
                address = f"{row['Ulice']}, {row['Místo']}"
                ruian = row["Kód RÚIAN"]
                school = ImportedSchool(
                    row["Zkrácený název"],
                    address.strip(" ,"),
                    "CZ",
                    row["Plný název"],
                    [],
                    row["IZO"],
                )

            if row["Typ"][0] == "B":
                school.types.append("zs")
            elif row["Typ"][0] == "C":
                school.types.extend(["ss", "6gym", "8gym"])
            else:
                continue

        if school:
            yield school
