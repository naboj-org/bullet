from django import forms
from django.core.validators import FileExtensionValidator
from django.db import transaction
from problems.logic.upload import handle_upload


class ProblemImportForm(forms.Form):
    file = forms.FileField(
        label="File to import", validators=[FileExtensionValidator(["zip"])]
    )

    def __init__(self, competition, **kwargs):
        super().__init__(**kwargs)
        self.competition = competition

    @transaction.atomic
    def save(self):
        handle_upload(self.competition, self.cleaned_data["file"])
