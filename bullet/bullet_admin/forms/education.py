from django import forms
from django.core.validators import FileExtensionValidator
from django_countries.fields import CountryField
from education.models import School

from bullet_admin.csv_import import SchoolCSVImporter, SchoolData
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

    def __init__(self, competition, user, **kwargs):
        super().__init__(**kwargs)
        self.fields["country"].choices = get_country_choices(competition, user)
        self.competition = competition
        self.user = user

    def get_data(self, max_rows: int | None = None) -> list[SchoolData]:
        return self.get_importer().get_data(max_rows=max_rows)

    def get_importer(self) -> SchoolCSVImporter:
        return SchoolCSVImporter(
            csv_file=self.cleaned_data["csv_file"],
        )


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
