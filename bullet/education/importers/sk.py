import csv
from typing import Iterable

from education.importers.base import BaseSchoolImporter, ImportedSchool


class SlovakSchoolImporter(BaseSchoolImporter):
    name = "sk"
    allowed_types = {
        "52N": "zs",  # ZŠ pre žiakov s nadaním
        "57N": "gym",  # Gymnázium pre žiakov s nadaním
        "115": "zs",  # MŠ - ZŠ s MŠ
        "116": "zs",  # MŠ - ZŠ s MŠ I.stupeň
        "211": "zs",  # Základná škola
        "213": "zs",  # ZŠ internátna
        "221": "zs",  # ZŠ I. stupeň
        "231": "zs",  # ZŠ II. stupeň
        "321": "gym",  # Gymnázium
        "341": "ss",  # Stredná športová škola (4R)
        "410": "ss5",  # Stredná odborná škola (2-5R)
        "416": "ss",  # Stredná priemyselná škola (4R)
        "451": "ss",  # Obchodná akadémia (4R)
        "452": "ss5",  # Hotelová akadémia (5R)
        "473": "ss",  # Škola umeleckého priemyslu (4R)
        "487": "ss",  # Stredná zdravotnícka škola (4R)
        # Špeciálne požiadavky
        "520": "zs",  # ZŠ pre žiakov s autizmom
        "522": "zs",  # ZŠ pre žiakov so sluchovým postihnutím
        "524": "zs",  # ZŠ pre žiakov s narušenou komunikačnou schopnosťou
        "525": "zs",  # ZŠ pre žiakov s telesným postihnutím
        "527": "zs",  # ZŠ pri zdravotníckom zariadení
        "528": "zs",  # ZŠ pri špeciálnom výchovnom zariadení
        "529": "zs",  # ZŠ pre žiakov s poruchou učenia
        "622": "zs",  # ZŠ pre žiakov so sluchovým postihnutím internátna
        "623": "zs",  # ZŠ pre žiakov so zrakovým postihnutím internátna
        "624": "zs",  # ZŠ pre žiakov s narušenou komunikačnou schopnosťou internátna
        "531": "zs10",  # Špeciálna základná škola
        "530": "zs10",  # ŠZŠ pre žiakov s autizmom
        "534": "zs10",  # ŠZŠ pre žiakov s narušenou komunikačnou schopnosťou
        "535": "zs10",  # ŠZŠ pre žiakov s telesným postihnutím
        "538": "zs10",  # ŠZŠ pri špeciálnom výchovnom zariadení
        "630": "zs10",  # ŠZŠ pre žiakov s autizmom internátna
        "631": "zs10",  # Špeciálna základná škola internátna
        "632": "zs10",  # ŠZŠ pre žiakov so sluchovým postihnutím internátna
        "633": "zs10",  # ŠZŠ pre žiakov so zrakovým postihnutím internátna
        "634": "zs10",  # ŠZŠ pre žiakov s narušenou komunikačnou schopnosťou int.
        "635": "zs10",  # ŠZŠ pre žiakov s telesným postihnutím internátna
        "636": "zs10",  # ŠZŠ pre hluchoslepých internátna
        "561": "ou",  # Odborné učilište
        "562": "ou",  # OU pre žiakov so sluchovým postihnutím
        "565": "ou",  # OU pre žiakov s telesným postihnutím
        "568": "ou",  # OU pri špec. výchov. zariadení
        "661": "ou",  # Odborné učilište internátne
        "662": "ou",  # OU pre žiakov sluchovo postihnutých internátne
        "663": "ou",  # OU pre žiakov so zrakovým postihnutím internátne
        "665": "ou",  # OU pre žiakov s telesným postihnutím internátne
        "582": "ss5",  # SOŠ pre žiakov so sluchovým postihnutím
        "585": "ss5",  # SOŠ pre žiakov s telesným postihnutím
        "588": "ss5",  # SOŠ pri špeciálnom výchovnom zariadení
        "682": "ss5",  # SOŠ pre  žiakov so sluchovým postihnutím internátna
        "683": "ss5",  # SOŠ pre žiakov so zrakovým postihnutím internátna
        "685": "ss5",  # SOŠ pre žiakov s telesným postihnutím internátna
        "575": "gym",  # Gymnázium pre žiakov s telesným postihnutím
        "672": "gym",  # Gymnázium pre sluchovo postihnutých internátne
    }

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
            "ou",
            "Odborné učilište",
            "OU (SK)",
            (f"{i}. ročník" for i in range(1, 4)),
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

    def get_schools(self) -> Iterable[ImportedSchool]:
        reader = csv.DictReader(self.file, delimiter=";")

        for row in reader:
            if row["STAV"] != "v prevádzke":
                continue
            if row["TypSaSZKod"] not in self.allowed_types:
                continue

            types = [self.allowed_types[row["TypSaSZKod"]]]
            address = f"{row['Ulica']} {row['OrientacneCislo']}, {row['Obec']}"

            if "gym" in types:
                types.append("8gym")

            if "biling" in row["VyucovaciJazyk"]:
                types.append("bilingval")

            yield ImportedSchool(
                row["NazovSkrateny"],
                address.strip(" ,"),
                "SK",
                row["Nazov"],
                types,
                row[reader.fieldnames[0]],
            )
