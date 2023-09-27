from typing import Type

from bullet_admin.forms.teams import OperatorTeamForm, SpanishTeamForm, TeamForm
from competitions.forms.registration import RegistrationForm, SpanishRegistrationForm
from django.forms import BaseForm


class RegistrationFlow:
    def get_form(self) -> Type[BaseForm]:
        """
        Returns the form used during registration.
        The form can have `save_related` method that gets called after the team
        gets saved.
        """
        return RegistrationForm

    def get_admin_form(self) -> Type[BaseForm]:
        """
        Returns the form used in the admin interface.
        """
        raise TeamForm

    def get_operator_form(self) -> Type[BaseForm]:
        """
        Returns the form used in the admin interface (for operators).
        """
        raise OperatorTeamForm

    def can_edit(self, team) -> bool:
        """
        Returns whether the team can be edited.
        This is AND-ed with normal requirements (eg. time).
        """
        return True

    def get_pre_registration_template(self) -> str | None:
        """
        Returns the name of template shown during registration before the registration
        form.
        """
        return None

    def get_post_registration_template(self) -> str | None:
        """
        Returns the name of template shown during registration after the registration
        form.
        """
        return None

    def get_pre_edit_template(self) -> str | None:
        """
        Returns the name of template shown during team editing before the team edit
        form.
        """
        return None

    def get_post_edit_template(self) -> str | None:
        """
        Returns the name of template shown during team editing after the team edit
        form.
        """
        return None

    def get_admin_row_template(self) -> str | None:
        """
        Returns the name of template shown in the admin's "Status" column in team list.
        """
        return None

    def get_admin_bottom_template(self) -> str | None:
        """
        Returns the name of template shown below the team edit form in admin.
        """
        return None


class SpanishRegistrationFlow(RegistrationFlow):
    def get_form(self) -> Type[BaseForm]:
        return SpanishRegistrationForm

    def can_edit(self, team) -> bool:
        return False

    def get_admin_row_template(self):
        return "bullet_admin/teams/list_spanish.html"

    def get_admin_bottom_template(self):
        return "bullet_admin/teams/edit_spanish.html"

    def get_admin_form(self) -> Type[BaseForm]:
        return SpanishTeamForm
