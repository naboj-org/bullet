from education.importers.es import SpanishSchoolImporter
from education.importers.sk import SlovakSchoolImporter

IMPORTERS = {
    "sk": SlovakSchoolImporter,
    "es": SpanishSchoolImporter,
}
