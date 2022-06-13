from competitions.branches import Branches
from django.conf import settings
from django.db import models


class LanguageField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs["choices"] = settings.LANGUAGES
        kwargs["max_length"] = 8
        super().__init__(*args, **kwargs)


class BranchField(models.IntegerField):
    def __init__(self, *args, **kwargs):
        kwargs["choices"] = Branches.choices()
        super().__init__(*args, **kwargs)
