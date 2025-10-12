from typing import TYPE_CHECKING

from competitions.branches import Branches
from competitions.models import Competition
from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint
from django_countries.fields import CountryField

from web.fields import (
    BranchField,
    ChoiceArrayField,
    IntegerChoiceArrayField,
    LanguageField,
)
from web.page_blocks.types import PAGE_BLOCK_TYPES, get_page_block_choices

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager


class Page(models.Model):
    id: int
    slug = models.SlugField(max_length=128)
    branch = BranchField()
    language = LanguageField()
    countries = ChoiceArrayField(CountryField())
    title = models.CharField(max_length=128)
    content = models.TextField(blank=True)

    pageblock_set: "RelatedManager[PageBlock]"

    def __str__(self):
        return self.title


class Menu(models.Model):
    url = models.CharField(max_length=128)
    branch = BranchField()
    language = LanguageField()
    countries = ChoiceArrayField(CountryField())
    title = models.CharField(max_length=128)
    order = models.IntegerField(default=1)
    is_external = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class ContentBlock(models.Model):
    group = models.CharField(max_length=256)
    reference = models.CharField(max_length=256)
    branch = BranchField(blank=True, null=True)
    country = CountryField(blank=True, null=True)
    language = models.CharField(choices=settings.LANGUAGES, max_length=8)
    content = models.TextField(blank=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=("group", "reference", "branch", "country", "language"),
                name="content_block__reference_unique",
            )
        ]

    def __str__(self):
        prefix = f"{self.group}:{self.reference} "
        if self.branch:
            branch = Branches[self.branch].short_name
            return prefix + f"({branch} {self.country.code}-{self.language})"
        return prefix + f"({self.country.code}-{self.language})"


class PageBlock(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    states = IntegerChoiceArrayField(
        models.IntegerField(choices=Competition.State.choices)
    )
    order = models.IntegerField()
    block_type = models.IntegerField(choices=get_page_block_choices())
    data = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ["page", "order"]

    @property
    def block(self):
        return PAGE_BLOCK_TYPES[self.block_type]

    @property
    def title(self) -> str:
        if not isinstance(self.data, dict):
            return ""
        if "title" not in self.data:
            return ""
        return self.data["title"]
