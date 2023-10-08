from django import forms
from education.models import School


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
