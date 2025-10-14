from typing import Any, Callable, Protocol

from competitions.models import Venue
from django.core.exceptions import ImproperlyConfigured
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponseNotFound
from users.models.organizers import User

from bullet_admin.utils import get_active_competition, get_redirect_url


class MixinProtocol(Protocol):
    request: HttpRequest
    get_context_data: Callable[..., dict]
    kwargs: dict[str, Any]
    get_object: Callable
    get_queryset: Callable
    get_model: Callable
    dispatch: Callable


class AuthedHttpRequest(HttpRequest):
    user: User  # type: ignore


class VenueMixin(MixinProtocol):
    """
    Sets self.venue to venue admin's venue or ?venue parameter
    if accessed by higher admin.
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


class IsOperatorContext(MixinProtocol):
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        competition = get_active_competition(self.request)
        crole = self.request.user.get_competition_role(competition)
        ctx["is_operator"] = crole.is_operator
        return ctx


class RedirectBackMixin(MixinProtocol):
    default_success_url = None

    def get_default_success_url(self) -> str:
        if self.default_success_url:
            return self.default_success_url

        raise ImproperlyConfigured(
            "No URL to redirect to. Provide a get_default_success_url."
        )

    def get_success_url(self):
        return get_redirect_url(self.request, self.get_default_success_url())
