from competitions.models import Competition
from countries.models import BranchCountry
from django import forms
from django.forms import ModelForm
from gallery.models import Album


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={"accept": "image/*"}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class AlbumForm(ModelForm):
    photo_files = MultipleFileField(required=False)

    class Meta:
        model = Album

        labels = {"photo_files": "Photos"}
        fields = ("competition", "title", "country")

    def __init__(self, **kwargs):
        branch = kwargs.pop("branch", None)
        super().__init__(**kwargs)
        self.fields["competition"].queryset = Competition.objects.filter(branch=branch)

        available_countries = set()

        for country in BranchCountry.objects.filter(branch=branch).all():
            available_countries.add(country.country.code)

        self.fields["country"].choices = list(
            sorted(
                filter(
                    lambda x: x[0] in available_countries,
                    self.fields["country"].choices,
                ),
                key=lambda x: x[1],
            )
        )
