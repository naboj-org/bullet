from bullet_admin.utils import get_active_competition
from competitions.models import Venue
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.urls import reverse


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


class AnyAdminRequiredMixin(AccessMixin):
    def can_access(self):
        competition = get_active_competition(self.request)
        if not competition:
            return False

        brole = self.request.user.get_branch_role(self.request.BRANCH)
        if brole.is_admin:
            return True

        crole = self.request.user.get_competition_role(competition)
        return crole.venue is not None or crole.country is not None


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
        return crole.can_delegate


class VenueMixin:
    """
    Sets self.venue to venue admin's venue or ?venue parameter
    if accessed by higher admin.

    Should be used after `AnyAdminRequiredMixin`.
    """

    def get_available_venues(self, request) -> QuerySet[Venue]:
        competition = get_active_competition(request)
        venue = Venue.objects.filter(
            category_competition__competition=competition
        ).select_related("category_competition")

        crole = request.user.get_competition_role(competition)
        if crole.venue:
            return venue.filter(id=crole.venue_id)

        if crole.country:
            venue = venue.filter(country=crole.country)

        return venue

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

        if (
            self.request.user.get_competition_role(
                get_active_competition(self.request)
            ).venue
            is None
        ):
            ctx["available_venues"] = self.available_venues
        return ctx
