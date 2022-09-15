from django.core.exceptions import ImproperlyConfigured, PermissionDenied


class RoleRequiredMixin:
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
            raise PermissionDenied("You don't have access to this page.")
        return super().dispatch(request, *args, **kwargs)
