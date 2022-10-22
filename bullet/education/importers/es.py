import csv
from typing import Iterable

from education.importers.base import BaseSchoolImporter, ImportedSchool


class SpanishSchoolImporter(BaseSchoolImporter):
    name = "es"

    types = (
        (
            "es",
            "Educación Secundaria Obligatoria",
            "ES",
            (f"{i}º E.S.O." for i in range(1, 5)),
        ),
    )

    def get_schools(self) -> Iterable[ImportedSchool]:
        reader = csv.DictReader(self.file)

        for row in reader:
            address = f"{row['Address']}, {row['City/Town']}"

            yield ImportedSchool(
                row["Name of the School"],
                address.strip(" ,"),
                "ES",
                "",
                ["es"],
                row["School Id."],
            )


class SpanishBachilleratoSchoolImporter(BaseSchoolImporter):
    name = "es-bach"

    types = (
        (
            "bachillerato",
            "Bachillerato",
            "ES",
            (f"{i}º Bachillerato" for i in range(1, 3)),
        ),
    )

    def get_schools(self) -> Iterable[ImportedSchool]:
        reader = csv.DictReader(self.file, delimiter=";")

        for row in reader:
            address = f"{row['DOMICILIO']}, {row['MUNICIPIO']}"

            yield ImportedSchool(
                row["CENTRO"],
                address.strip(" ,"),
                "ES",
                "",
                ["bachillerato"],
                row["CODIGO CENTRO"],
            )
