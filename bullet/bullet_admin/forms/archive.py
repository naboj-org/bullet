from bullet_admin.forms.utils import get_language_choices
from django import forms
from django.core.files.storage import default_storage
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


class ProblemUploadForm(forms.Form):
    language = forms.ChoiceField(label="Language")
    file = forms.FileField(
        label="Problem statements", validators=[FileExtensionValidator(["pdf"])]
    )

    def __init__(self, competition, **kwargs):
        super().__init__(**kwargs)
        self.competition = competition
        self.fields["language"].choices = get_language_choices(competition.branch)

    @transaction.atomic
    def save(self):
        file = self.cleaned_data.get("file")
        path = (
            self.competition.secret_dir
            / f"problems-{self.cleaned_data.get('language').lower()}.pdf"
        )
        if default_storage.exists(path):
            default_storage.delete(path)
        default_storage.save(path, file)
