from operator import itemgetter

from competitions.models.competitions import Competition
from countries.models import BranchCountry
from django import forms
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


class AlbumUploadForm(forms.Form):
    photo_files = MultipleFileField(required=False, label="Photos")


class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ("title", "slug", "country")
        labels = {"slug": "URL suffix"}
        help_texts = {
            "title": "You don't need to include year here.",
            "slug": "You don't need to include year here.",
        }

    def __init__(self, competition: Competition, **kwargs):
        super().__init__(**kwargs)
        self.competition = competition

        available_countries = set()
        for country in BranchCountry.objects.filter(branch=competition.branch).all():
            available_countries.add(country.country.code)

        countries = []
        for code, name in self.fields["country"].choices:
            if code in available_countries:
                countries.append((code, name))
        countries.sort(key=itemgetter(1))
        self.fields["country"].choices = countries

    def clean_slug(self):
        slug = self.cleaned_data["slug"]

        qs = Album.objects.filter(slug=slug, competition=self.competition)
        if self.instance.id:
            qs = qs.exclude(id=self.instance.id)

        if qs.exists():
            raise forms.ValidationError("This URL is already in use.")

        return slug

    def save(self, commit: bool = True):
        obj = super().save(False)
        obj.competition = self.competition

        if commit:
            obj.save()
        return obj
