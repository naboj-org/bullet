from competitions.branches import Branch
from countries.models import BranchCountry
from django import forms
from web.models import ContentBlock, Logo, Menu, Page


class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ("title", "slug", "language", "countries", "content")

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
            sorted(
                filter(
                    lambda x: x[0] in available_languages,
                    self.fields["language"].choices,
                ),
                key=lambda x: x[1],
            )
        )
        self.fields["countries"].choices = list(
            sorted(
                filter(
                    lambda x: x[0] in available_countries,
                    self.fields["countries"].choices,
                ),
                key=lambda x: x[1],
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
            sorted(
                filter(
                    lambda x: x[0] in available_languages,
                    self.fields["language"].choices,
                ),
                key=lambda x: x[1],
            )
        )
        self.fields["country"].choices = list(
            sorted(
                filter(
                    lambda x: x[0] == "" or x[0] in available_countries,
                    self.fields["country"].choices,
                ),
                key=lambda x: x[1],
            )
        )


class ContentBlockWithRefForm(ContentBlockForm):
    class Meta(ContentBlockForm.Meta):
        fields = ("group", "reference", "language", "country", "content")


class LogoForm(forms.ModelForm):
    class Meta:
        model = Logo
        fields = ("type", "name", "url", "image", "countries")

        widgets = {
            "countries": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, branch: Branch, **kwargs):
        super().__init__(**kwargs)
        available_countries = set()

        for country in BranchCountry.objects.filter(branch=branch).all():
            available_countries.add(country.country.code)

        self.fields["countries"].choices = list(
            sorted(
                filter(
                    lambda x: x[0] in available_countries,
                    self.fields["countries"].choices,
                ),
                key=lambda x: x[1],
            )
        )


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = (
            "title",
            "url",
            "order",
            "is_external",
            "is_visible",
            "language",
            "countries",
        )

        widgets = {
            "countries": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, branch: Branch, **kwargs):
        super().__init__(**kwargs)
        available_countries = set()
        available_languages = set()

        for country in BranchCountry.objects.filter(branch=branch).all():
            available_countries.add(country.country.code)
            available_languages.update(country.languages)

        self.fields["language"].choices = list(
            sorted(
                filter(
                    lambda x: x[0] in available_languages,
                    self.fields["language"].choices,
                ),
                key=lambda x: x[1],
            )
        )

        self.fields["countries"].choices = list(
            sorted(
                filter(
                    lambda x: x[0] in available_countries,
                    self.fields["countries"].choices,
                ),
                key=lambda x: x[1],
            )
        )
