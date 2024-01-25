from django import forms

from bullet_admin.fields import FileBrowserInput


class FolderCreateForm(forms.Form):
    path = forms.CharField(disabled=True, required=False, label="Parent path")
    name = forms.SlugField(label="Name")

    def __init__(self, **kwargs):
        initial_path = kwargs.pop("initial_path")
        super().__init__(**kwargs)
        self.fields["path"].initial = initial_path


class FileUploadForm(forms.Form):
    path = forms.CharField(disabled=True, required=False, label="Parent path")
    name = forms.CharField(
        label="Name",
        required=False,
        help_text="Leave empty to use uploaded file's name.",
    )
    file = forms.FileField(label="File")

    def __init__(self, **kwargs):
        initial_path = kwargs.pop("initial_path")
        super().__init__(**kwargs)
        self.fields["path"].initial = initial_path


class FileDeleteForm(forms.Form):
    path = forms.CharField(disabled=True, required=False, label="Path")

    def __init__(self, **kwargs):
        initial_path = kwargs.pop("initial_path")
        super().__init__(**kwargs)
        self.fields["path"].initial = initial_path


class TestForm(forms.Form):
    path = forms.CharField(label="Path", widget=FileBrowserInput())
