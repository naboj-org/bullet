from django import forms
from education.models import School


class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ["name", "address", "country", "search", "types"]
        widgets = {
            "types": forms.CheckboxSelectMultiple(),
        }
