from education.importers.cz import CzechSchoolImporter
from education.importers.es import SpanishSchoolImporter
from education.importers.hr import CroatianSchoolImporter
from education.importers.pl import PolishSchoolImporter
from education.importers.sk import SlovakSchoolImporter

IMPORTERS = {
    "sk": SlovakSchoolImporter,
    "cz": CzechSchoolImporter,
    "es": SpanishSchoolImporter,
    "pl": PolishSchoolImporter,
    "hr": CroatianSchoolImporter,
}
