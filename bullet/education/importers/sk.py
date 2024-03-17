import csv
from typing import Iterable

from education.importers.base import BaseSchoolImporter, ImportedSchool


class SlovakSchoolImporter(BaseSchoolImporter):
    name = "sk"

    types = (
        (
            "zs",
            "Základná škola",
            "ZŠ (SK)",
            (f"{i}. ročník" for i in range(1, 10)),
        ),
        (
            "gym",
            "Gymnázium",
            "4GYM (SK)",
            (f"{i}. ročník" for i in range(1, 5)),
        ),
        (
            "ss",
            "Stredná škola",
            "SŠ (SK)",
            (f"{i}. ročník" for i in range(1, 5)),
        ),
        (
            "ss5",
            "Stredná škola (5-ročná)",
            "SŠ5 (SK)",
            (f"{i}. ročník" for i in range(1, 6)),
        ),
        (
            "zs10",
            "Základná škola (10-ročná)",
            "ZŠ10 (SK)",
            (f"{i}. ročník" for i in range(1, 11)),
        ),
        (
            "8gym",
            "Osemročné gymnázium",
            "8GYM (SK)",
            (
                "Príma",
                "Sekunda",
                "Tercia",
                "Kvarta",
                "Kvinta",
                "Sexta",
                "Septima",
                "Oktáva",
            ),
        ),
        (
            "bilingval",
            "Bilingválne štúdium",
            "Biling (SK)",
            (f"{i}. ročník" for i in range(1, 6)),
        ),
    )

    type_mapping = {
        "gym": "gym",
        "gym:4": "gym",
        "gym:5": "bilingval",
        "gym:8": "8gym",
        "ss:4": "ss",
        "ss": "ss",
        "ss:5": "ss5",
        "zs": "zs",
        "zs:9": "zs",
        "zs:10": "zs10",
    }

    def get_schools(self) -> Iterable[ImportedSchool]:
        reader = csv.DictReader(self.file)

        for row in reader:
            years = row["years"].split(",")

            types = []
            for year in years:
                if year not in self.type_mapping:
                    continue
                types.append(self.type_mapping[year])

            yield ImportedSchool(
                row["name"],
                row["address"],
                "SK",
                "",
                types,
                row["eduid"],
            )
