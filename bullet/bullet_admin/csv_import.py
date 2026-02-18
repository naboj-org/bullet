import csv
import os
from dataclasses import dataclass
from functools import partial
from io import TextIOWrapper
from uuid import uuid4

from django.core.files.storage import default_storage
from django.db import transaction
from django.template.loader import render_to_string
from education.models import School, SchoolType


@dataclass
class SchoolData:
    identifier: str
    name: str
    address: str
    types: list[str]


class SchoolCSVImporter:
    REQUIRED_COLUMNS = ["identifier", "name", "address", "types"]

    def __init__(self, csv_file, country):
        self.csv_file = csv_file
        self.country = country

    def _read_csv_rows(self, max_rows: int | None = None) -> list[dict]:
        rows = []
        with TextIOWrapper(self.csv_file.file, encoding="utf-8") as decoded_file:
            self.csv_file.file.seek(0)

            reader = csv.DictReader(decoded_file)
            if not reader.fieldnames:
                raise ValueError("CSV file has no header row")

            # Validate required columns
            missing_columns = [
                col for col in self.REQUIRED_COLUMNS if col not in reader.fieldnames
            ]
            if missing_columns:
                raise ValueError(
                    f"CSV file is missing required columns: {', '.join(missing_columns)}."
                )

            for i, row in enumerate(reader):
                if max_rows is not None and i >= max_rows:
                    break
                rows.append(row)

        return rows

    def _parse_row(self, row: dict) -> SchoolData:
        identifier = row.get("identifier", "").strip()
        name = row.get("name", "").strip()
        address = row.get("address", "").strip()
        types_str = row.get("types", "").strip()
        types = [t.strip() for t in types_str.split(",") if t.strip()]

        return SchoolData(identifier, name, address, types)

    def get_data(self, max_rows: int | None = None) -> list[SchoolData]:
        rows = self._read_csv_rows(max_rows=max_rows)
        return [self._parse_row(row) for row in rows]

    @transaction.atomic
    def import_schools(self) -> dict:
        schools_data = self.get_data()

        if not schools_data:
            raise ValueError("No valid school data found in CSV file")

        created_count = 0
        updated_count = 0
        errors = []

        # Cache school types
        school_types_cache = {}
        used_types = set()
        for data in schools_data:
            used_types.update(data.types)

        for type_name in used_types:
            school_type = SchoolType.objects.filter(identifier=type_name).first()
            if not school_type:
                continue
            school_types_cache[type_name] = school_type

        # Import schools
        school_ids = []
        for data in schools_data:
            school = None
            if data.identifier:
                school = School.objects.filter(
                    importer_identifier=data.identifier,
                    country=self.country,
                ).first()

            if school:
                if school.importer_ignored:
                    errors.append(f"School {school.importer_identifier} is ignored")
                    continue
                updated_count += 1
            else:
                school = School(
                    importer_identifier=data.identifier,
                    country=self.country,
                )
                created_count += 1

            school.name = data.name
            school.address = data.address
            school.save(send_to_search=False)

            types = [
                school_types_cache[type_name]
                for type_name in data.types
                if type_name in school_types_cache
            ]
            school.types.set(types)

            school_ids.append(school.id)

        from education.tasks import send_schools_to_search

        transaction.on_commit(partial(send_schools_to_search, school_ids=school_ids))

        return {
            "created": created_count,
            "updated": updated_count,
            "errors": errors,
            "total": len(schools_data),
        }


def save_csv_file(csv_file) -> str:
    filename = f"school_import_{uuid4().hex}.csv"
    path = os.path.join("school_imports", filename)

    # Delete if exists (unlikely with UUID)
    if default_storage.exists(path):
        default_storage.delete(path)

    saved_path = default_storage.save(path, csv_file)
    return saved_path


def get_csv_file_path(saved_path: str) -> str:
    return default_storage.path(saved_path)


def send_import_result_email(user_email: str, result: dict):
    """
    Send a plain text email with the import results to the user.
    """
    from django.conf import settings
    from django.core.mail import send_mail

    subject = "School CSV import result"

    context = {
        "result": result,
    }

    message = render_to_string("bullet_admin/emails/school_import_result.txt", context)

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )
