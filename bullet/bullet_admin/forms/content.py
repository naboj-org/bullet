from competitions.branches import Branch
from countries.models import BranchCountry
from django import forms
from django.core.exceptions import ValidationError
from django_countries import countries
from web.models import ContentBlock, Logo, Menu, Page, PageBlock


class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ("title", "slug", "language", "countries", "content")

        widgets = {
            "countries": forms.CheckboxSelectMultiple(),
            "content": forms.Textarea(attrs={"rows": 30}),
        }

        labels = {
            "slug": "URL",
        }

        help_texts = {
            "slug": "The part after naboj.org/xx/xx/.",
        }

    def __init__(self, branch: Branch, **kwargs):
        super().__init__(**kwargs)
        self._branch = branch
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

    def clean(self):
        data = super().clean()

        qs = Page.objects
        if self.instance:
            qs = qs.exclude(id=self.instance.id)

        if qs.filter(
            slug=data.get("slug"),
            branch=self._branch,
            countries__overlap=data.get("countries"),
            language=data.get("language"),
        ).exists():
            raise ValidationError("Page with the same slug already exists.")

        for country in data.get("countries"):
            if not BranchCountry.objects.filter(
                branch=self._branch,
                country=country,
                languages__contains=[data.get("language")],
            ).exists():
                raise ValidationError(
                    f"This language cannot be used in {countries.name(country)}."
                )

        return data


class ContentBlockForm(forms.ModelForm):
    class Meta:
        model = ContentBlock
        fields = ("language", "country", "content")

    def __init__(self, branch: Branch, **kwargs):
        super().__init__(**kwargs)
        self._branch = branch
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

    def clean(self):
        data = super().clean()

        if (
            data.get("country")
            and not BranchCountry.objects.filter(
                branch=self._branch,
                country=data.get("country"),
                languages__contains=[data.get("language")],
            ).exists()
        ):
            raise ValidationError("This language cannot be used in this country.")

        return data


class ContentBlockWithRefForm(ContentBlockForm):
    class Meta(ContentBlockForm.Meta):
        fields = ("group", "reference", "language", "country", "content")

    def clean(self):
        cleaned_data = super().clean()

        qs = ContentBlock.objects
        if self.instance:
            qs = qs.exclude(id=self.instance.id)

        if qs.filter(
            group=cleaned_data.get("group"),
            reference=cleaned_data.get("reference"),
            branch=self._branch,
            country=cleaned_data.get("country"),
            language=cleaned_data.get("language"),
        ).exists():
            raise ValidationError("This content block already exists.")

        return cleaned_data


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
        self._branch = branch
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

    def clean(self):
        data = super().clean()

        for country in data.get("countries"):
            if not BranchCountry.objects.filter(
                branch=self._branch,
                country=country,
                languages__contains=[data.get("language")],
            ).exists():
                raise ValidationError(
                    f"This language cannot be used in {countries.name(country)}."
                )

        return data


class PageBlockUpdateForm(forms.ModelForm):
    class Meta:
        model = PageBlock
        fields = ["states", "order"]

        labels = {"states": "Visibility", "order": "Order"}

        help_texts = {"order": "Blocks are shown in ascending order."}

        widgets = {"states": forms.CheckboxSelectMultiple()}
