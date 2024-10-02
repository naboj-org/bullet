from education.importers.at_zs import AustrianPrimarySchoolImporter
from education.importers.be import BelgianSchoolImporter
from education.importers.cz import CzechSchoolImporter
from education.importers.es import (
    SpanishBachilleratoSchoolImporter,
    SpanishSchoolImporter,
)
from education.importers.fr import FrenchSchoolImporter
from education.importers.hr import CroatianSchoolImporter
from education.importers.hu import HungarianSchoolImporter
from education.importers.nl import DutchSchoolImporter
from education.importers.old import OldSchoolImporter
from education.importers.old_ro import RomanianSchoolImporter
from education.importers.pl import PolishSchoolImporter
from education.importers.rs import SerbianSchoolImporter
from education.importers.sk import SlovakSchoolImporter
from education.importers.wales import WalesSchoolImporter

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
    "be": BelgianSchoolImporter,
    "old": OldSchoolImporter,
    "wales": WalesSchoolImporter,
    "old_ro": RomanianSchoolImporter,
    "rs": SerbianSchoolImporter,
    "at_zs": AustrianPrimarySchoolImporter,
}
