from competitions.branches import Branches
from django import forms
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
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


class ChoiceArrayField(ArrayField):
    def formfield(self, **kwargs):
        defaults = {
            "form_class": forms.MultipleChoiceField,
            "choices": self.base_field.choices,
        }
        defaults.update(kwargs)
        return super(ArrayField, self).formfield(**defaults)


class IntegerChoiceArrayField(ArrayField):
    def formfield(self, **kwargs):
        defaults = {
            "form_class": forms.TypedMultipleChoiceField,
            "coerce": int,
            "choices": self.base_field.choices,
        }
        defaults.update(kwargs)
        return super(ArrayField, self).formfield(**defaults)
