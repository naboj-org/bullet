from competitions.models import Venue
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.db.models import QuerySet
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.urls import reverse

from bullet_admin.utils import get_active_competition, get_redirect_url, is_admin


class AccessMixin:
    def can_access(self):
        raise NotImplementedError()

    def handle_fail(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("You don't have access to this page.")
        return HttpResponseRedirect(reverse("badmin:login"))

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_anonymous or not self.can_access():
            return self.handle_fail()
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(AccessMixin):
    def can_access(self):
        competition = get_active_competition(self.request)
        if not competition:
            return False

        return is_admin(self.request.user, competition)


class OperatorRequiredMixin(AccessMixin):
    def can_access(self):
        competition = get_active_competition(self.request)
        if not competition:
            return False

        brole = self.request.user.get_branch_role(self.request.BRANCH)
        if brole.is_admin:
            return True

        crole = self.request.user.get_competition_role(competition)
        return crole.venues or crole.countries


class TranslatorRequiredMixin(AccessMixin):
    def can_access(self):
        role = self.request.user.get_branch_role(self.request.BRANCH)
        return role.is_translator


class DelegateRequiredMixin(AccessMixin):
    def can_access(self):
        role = self.request.user.get_branch_role(self.request.BRANCH)
        if role.is_admin:
            return True

        competition = get_active_competition(self.request)
        if not competition:
            return False

        crole = self.request.user.get_competition_role(competition)
        return crole.can_delegate and not crole.is_operator


class VenueMixin:
    """
    Sets self.venue to venue admin's venue or ?venue parameter
    if accessed by higher admin.

    Should be used after `AnyAdminRequiredMixin`.
    """

    def get_available_venues(self, request) -> QuerySet[Venue]:
        return Venue.objects.for_request(request)

    def get_venue(self, request) -> Venue:
        if "venue" in request.GET:
            return self.available_venues.filter(id=request.GET["venue"]).first()

        return self.available_venues.first()

    def dispatch(self, request, *args, **kwargs):
        self.available_venues = self.get_available_venues(request)
        self.venue = self.get_venue(request)

        if not self.venue:
            return HttpResponseNotFound()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx["venue"] = self.venue

        # 0 -> higher admin, 1 -> one venue admin, 2+ -> multiple venue admin
        if (
            len(
                self.request.user.get_competition_role(
                    get_active_competition(self.request)
                ).venues
            )
            != 1
        ):
            ctx["available_venues"] = self.available_venues
        return ctx


class IsOperatorContext:
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        competition = get_active_competition(self.request)
        crole = self.request.user.get_competition_role(competition)
        ctx["is_operator"] = crole.is_operator
        return ctx


class RedirectBackMixin:
    def get_default_success_url(self):
        raise ImproperlyConfigured(
            "No URL to redirect to. Provide a get_default_success_url."
        )

    def get_success_url(self):
        return get_redirect_url(self.request, self.get_default_success_url())
