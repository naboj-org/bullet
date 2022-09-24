from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse


class AccessMixin:
    def handle_fail(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("You don't have access to this page.")
        return HttpResponseRedirect(reverse("badmin:login"))


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
