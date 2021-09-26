from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class OldSite:
    id_site: int
    id_country: int
    name: str
    short_name: str


OldSite.table_name = 'naboj_site'
