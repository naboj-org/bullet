from bullet_admin.utils import get_active_competition
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse


class AccessMixin:
    def handle_fail(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("You don't have access to this page.")
        return HttpResponseRedirect(reverse("badmin:login"))


class AnyAdminRequiredMixin(AccessMixin):
    def is_admin(self):
        if self.request.user.is_anonymous:
            return False

        competition = get_active_competition(self.request)
        if not competition:
            return False

        brole = self.request.user.get_branch_role(self.request.BRANCH)
        if brole.is_admin:
            return True

        crole = self.request.user.get_competition_role(competition)
        return crole.venue is not None or crole.country is not None

    def dispatch(self, request, *args, **kwargs):
        if not self.is_admin():
            return self.handle_fail()
        return super().dispatch(request, *args, **kwargs)


class TranslatorRequiredMixin(AccessMixin):
    def is_translator(self):
        if self.request.user.is_anonymous:
            return False

        role = self.request.user.get_branch_role(self.request.BRANCH)
        return role.is_translator

    def dispatch(self, request, *args, **kwargs):
        if not self.is_translator():
            return self.handle_fail()
        return super().dispatch(request, *args, **kwargs)
