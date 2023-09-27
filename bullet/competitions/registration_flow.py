from typing import Type

from competitions.forms.registration import RegistrationForm, SpanishRegistrationForm
from django.forms import Form


class RegistrationFlow:
    def get_form(self) -> Type[Form]:
        return RegistrationForm

    def get_admin_form(self) -> Type[Form] | None:
        raise NotImplementedError

    def can_edit(self, team) -> bool:
        return True

    def get_pre_registration_template(self) -> str | None:
        return None

    def get_post_registration_template(self) -> str | None:
        return None

    def get_pre_edit_template(self) -> str | None:
        return None

    def get_post_edit_template(self) -> str | None:
        return None

    def get_admin_row_template(self) -> str | None:
        return None


class SpanishRegistrationFlow(RegistrationFlow):
    def get_admin_row_template(self):
        return "test.html"

    def get_form(self) -> Type[Form]:
        return SpanishRegistrationForm

    def can_edit(self, team) -> bool:
        return False
