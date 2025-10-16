import csv
from dataclasses import dataclass
from functools import partial
from io import TextIOWrapper

from django import forms
from django.core.validators import FileExtensionValidator
from django.db import transaction
from django_countries.fields import CountryField
from education.models import School, SchoolType
from education.tasks import send_schools_to_search

from bullet_admin.forms.utils import get_country_choices


class SchoolCSVImportForm(forms.Form):
    csv_file = forms.FileField(
        label="CSV file",
        validators=[FileExtensionValidator(["csv"])],
        help_text="CSV format: identifier, name, address, types (comma-separated)",
    )
    country = CountryField().formfield()
    preview = forms.BooleanField(
        label="Preview only (don't import)",
        required=False,
        initial=True,
        help_text="Check this to preview the import without making changes",
    )

    @dataclass
    class SchoolData:
        identifier: str
        name: str
        address: str
        types: list[str]

    def __init__(self, competition, user, **kwargs):
        super().__init__(**kwargs)
        self.fields["country"].choices = get_country_choices(competition, user)
        self.competition = competition
        self.user = user

    def parse_csv(self) -> list[SchoolData]:
        csv_file = self.cleaned_data["csv_file"]

        schools = []
        with TextIOWrapper(csv_file.file, encoding="utf-8") as decoded_file:
            csv_file.file.seek(0)

            reader = csv.DictReader(decoded_file)
            if not reader.fieldnames:
                raise ValueError("CSV file has no header row")

            required_columns = ["identifier", "name", "address", "types"]
            missing_columns = []
            for col in required_columns:
                if col not in reader.fieldnames:
                    missing_columns.append(col)
            if missing_columns:
                raise ValueError(
                    f"CSV file is missing required columns: {', '.join(missing_columns)}."
                )

            for row in reader:
                identifier = row.get("identifier", "").strip()
                name = row.get("name", "").strip()
                address = row.get("address", "").strip()
                types_str = row.get("types", "").strip()
                types = [t.strip() for t in types_str.split(",") if t.strip()]

                schools.append(
                    SchoolCSVImportForm.SchoolData(identifier, name, address, types)
                )

        if not schools:
            raise ValueError("No valid school data found in CSV file")
        return schools

    @transaction.atomic
    def import_schools(self):
        schools_data = self.parse_csv()
        country = self.cleaned_data["country"]

        created_count = 0
        updated_count = 0
        errors = []

        school_types_cache = {}
        used_types = set()
        for data in schools_data:
            used_types.update(data.types)

        for type_name in used_types:
            school_type = SchoolType.objects.filter(identifier=type_name).first()
            if not school_type:
                continue
            school_types_cache[type_name] = school_type

        school_ids = []
        for data in schools_data:
            school = None
            if data.identifier:
                school = School.objects.filter(
                    importer_identifier=data.identifier,
                    country=country,
                ).first()

            if school:
                if school.importer_ignored:
                    errors.append(f"School {school.importer_identifier} is ignored")
                    continue
                updated_count += 1
            else:
                school = School(
                    importer_identifier=data.identifier,
                    country=country,
                )
                created_count += 1

            school.name = data.name
            school.address = data.address
            school.save(send_to_search=False)

            types = []
            for type_name in data.types:
                if type_name in school_types_cache:
                    types.append(school_types_cache[type_name])
            school.types.set(types)

            school_ids.append(school.id)

        transaction.on_commit(partial(send_schools_to_search, school_ids=school_ids))

        return {
            "created": created_count,
            "updated": updated_count,
            "errors": errors,
            "total": len(schools_data),
        }


class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ["name", "address", "country", "search", "types", "is_hidden"]
        widgets = {
            "types": forms.CheckboxSelectMultiple(),
        }
        labels = {"is_hidden": "Is hidden?"}
        help_texts = {
            "is_hidden": "Hides the school from school search during team "
            "registration.",
            "search": "You can add any extra words or phrases that won't be shown, but "
            "will get used by the search engine.",
        }

    def __init__(self, competition, user, **kwargs):
        super().__init__(**kwargs)
        self.fields["country"].choices = get_country_choices(competition, user)
