from education.importers.cz import CzechSchoolImporter
from education.importers.es import (
    SpanishBachilleratoSchoolImporter,
    SpanishSchoolImporter,
)
from education.importers.fr import FrenchSchoolImporter
from education.importers.hr import CroatianSchoolImporter
from education.importers.hu import HungarianSchoolImporter
from education.importers.nl import DutchSchoolImporter
from education.importers.pl import PolishSchoolImporter
from education.importers.sk import SlovakSchoolImporter

IMPORTERS = {
    "sk": SlovakSchoolImporter,
    "cz": CzechSchoolImporter,
    "es": SpanishSchoolImporter,
    "es-bach": SpanishBachilleratoSchoolImporter,
    "pl": PolishSchoolImporter,
    "hr": CroatianSchoolImporter,
    "fr": FrenchSchoolImporter,
    "hu": HungarianSchoolImporter,
    "nl": DutchSchoolImporter,
}
