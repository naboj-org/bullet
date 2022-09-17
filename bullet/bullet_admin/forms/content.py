from competitions.branches import Branch
from countries.models import BranchCountry
from django import forms
from web.models import ContentBlock, Page


class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ("title", "slug", "language", "countries", "content")

        help_texts = {
            "content": "Supports Markdown syntax.",
        }

        widgets = {
            "countries": forms.CheckboxSelectMultiple(),
            "content": forms.Textarea(attrs={"rows": 30}),
        }

    def __init__(self, branch: Branch, **kwargs):
        super().__init__(**kwargs)
        available_countries = set()
        available_languages = set()

        for country in BranchCountry.objects.filter(branch=branch).all():
            available_countries.add(country.country.code)
            available_languages.update(country.languages)

        self.fields["language"].choices = list(
            filter(
                lambda x: x[0] in available_languages, self.fields["language"].choices
            )
        )
        self.fields["countries"].choices = list(
            filter(
                lambda x: x[0] in available_countries, self.fields["countries"].choices
            )
        )


class ContentBlockForm(forms.ModelForm):
    class Meta:
        model = ContentBlock
        fields = ("language", "country", "content")

    def __init__(self, branch: Branch, **kwargs):
        super().__init__(**kwargs)
        available_countries = set()
        available_languages = set()

        for country in BranchCountry.objects.filter(branch=branch).all():
            available_countries.add(country.country.code)
            available_languages.update(country.languages)

        self.fields["language"].choices = list(
            filter(
                lambda x: x[0] in available_languages, self.fields["language"].choices
            )
        )
        self.fields["country"].choices = list(
            filter(
                lambda x: x[0] == "" or x[0] in available_countries,
                self.fields["country"].choices,
            )
        )


class ContentBlockWithRefForm(ContentBlockForm):
    class Meta(ContentBlockForm.Meta):
        fields = ("group", "reference", "language", "country", "content")
