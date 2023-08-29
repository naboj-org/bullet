import hashlib
from dataclasses import dataclass
from typing import IO, Iterable

from education.models import Grade, School, SchoolType


@dataclass
class ImportedSchool:
    name: str
    address: str
    country: str
    search: str
    types: list[str]
    identifier: str | None

    def get_identifier(self):
        if self.identifier:
            return self.identifier
        key = f"{self.name.strip()},{self.address.strip()}".encode("utf-8")
        return hashlib.sha1(key).hexdigest()


@dataclass
class ImportResult:
    created: int = 0
    updated: int = 0
    lost_identifiers: set[str] | None = None


class BaseSchoolImporter:
    name = ""
    types = ()

    def __init__(self, file: IO):
        self.file = file
        if not self.name:
            raise ValueError("School importer does not have proper name.")
        self.type_objects = {}

    def get_schools(self) -> Iterable[ImportedSchool]:
        raise NotImplementedError()

    def prepare_types(self):
        for typ in self.types:
            ident = f"{self.name}-{typ[0]}"
            obj, _ = SchoolType.objects.update_or_create(
                identifier=ident,
                defaults={"name": typ[1], "note": typ[2]},
            )

            for i, grade in enumerate(typ[3]):
                Grade.objects.update_or_create(
                    school_type=obj, order=i, defaults={"name": grade}
                )

            self.type_objects[ident] = obj

    def import_schools(self) -> ImportResult:
        res = ImportResult()
        res.lost_identifiers = set(
            School.objects.filter(importer=self.name).values_list(
                "importer_identifier", flat=True
            )
        )

        for school in self.get_schools():
            ident = school.get_identifier()

            try:
                obj = School.objects.get(
                    importer=self.name,
                    importer_identifier=ident,
                )
                res.updated += 1
            except School.DoesNotExist:
                obj = School(
                    importer=self.name,
                    importer_identifier=ident,
                )
                res.created += 1

            # Skip importing schools that were manually edited.
            if obj.importer_ignored:
                continue

            obj.name = school.name.strip()
            obj.address = school.address.strip()
            obj.country = school.country
            obj.search = school.search
            obj.save(send_to_search=False)

            if ident in res.lost_identifiers:
                res.lost_identifiers.remove(ident)

            current = set(obj.types.values_list("identifier", flat=True))
            new = set([f"{self.name}-{x}" for x in school.types])

            obj.types.through.objects.filter(
                schooltype__identifier__in=current.difference(new)
            ).delete()
            for school_type in new.difference(current):
                if school_type not in self.type_objects:
                    raise ValueError(f"School type {school_type} is unknown.")
                obj.types.add(self.type_objects[school_type])
        return res
