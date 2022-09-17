from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse


class AccessMixin:
    def handle_fail(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("You don't have access to this page.")
        return HttpResponseRedirect(reverse("badmin:login"))


class RoleRequiredMixin(AccessMixin):
    role_required = None

    def has_role(self):
        if self.role_required is None:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} is missing the role_required attribute."
            )

        if self.request.user.is_anonymous:
            return False

        role = self.request.user.get_role(self.request.BRANCH)
        return role.role in self.role_required

    def dispatch(self, request, *args, **kwargs):
        if not self.has_role():
            return self.handle_fail()
        return super().dispatch(request, *args, **kwargs)


class TranslatorRequiredMixin(AccessMixin):
    def is_translator(self):
        if self.request.user.is_anonymous:
            return False

        role = self.request.user.get_role(self.request.BRANCH)
        return role.can_translate

    def dispatch(self, request, *args, **kwargs):
        if not self.is_translator():
            return self.handle_fail()
        return super().dispatch(request, *args, **kwargs)
