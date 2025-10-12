from inspect import signature
from typing import Callable

from competitions.models.competitions import Competition
from competitions.models.venues import Venue
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from users.models.organizers import User

from bullet_admin.mixins import MixinProtocol
from bullet_admin.utils import get_active_competition


def competition_is_unlocked(user: User, competition: Competition) -> bool:
    """The competition must be unlocked."""
    return not competition.results_public


def is_branch_admin(user: User, competition: Competition) -> bool:
    """You must be a branch administrator of the competition."""
    if user.is_superuser:
        return True

    brole = user.get_branch_role(competition.branch)
    return brole.is_admin


def is_country_admin(user: User, competition: Competition) -> bool:
    """You must be a country administrator or higher in the competition."""
    if is_branch_admin(user, competition):
        return True

    crole = user.get_competition_role(competition)
    return not crole.is_operator and bool(crole.countries)


def is_admin(user: User, competition: Competition) -> bool:
    """You must be a venue administrator or higher in the competition."""
    if is_country_admin(user, competition):
        return True

    crole = user.get_competition_role(competition)
    return not crole.is_operator and bool(crole.venues)


def is_operator(user: User, competition: Competition) -> bool:
    """You must be a operator or higher in the competition."""
    if is_admin(user, competition):
        return True

    crole = user.get_competition_role(competition)
    return crole.is_operator


def is_branch_admin_in(user: User, venue: Venue) -> bool:
    """You must be a branch administrator of the venue."""
    return is_branch_admin(user, venue.category.competition)


def is_country_admin_in(user: User, venue: Venue) -> bool:
    """You must be a contry administrator or higher of the venue."""
    if is_branch_admin_in(user, venue.category.competition):
        return True

    crole = user.get_competition_role(venue.category.competition)
    if crole.is_operator:
        return False

    if not crole.countries:
        return False

    return venue.country in crole.countries


def is_admin_in(user: User, venue: Venue) -> bool:
    """You must be a venue administrator or higher of the venue."""
    if is_country_admin_in(user, venue):
        return True

    crole = user.get_competition_role(venue.category.competition)
    if crole.is_operator:
        return False

    return venue in crole.venues


def is_operator_in(user: User, venue: Venue) -> bool:
    """You must be a operator or higher of the venue."""
    if is_admin_in(user, venue):
        return True

    crole = user.get_competition_role(venue.category.competition)
    return venue in crole.venues


type CompetitionPermissionCallable = Callable[[User, Competition], bool]
type VenuePermissionCallable = Callable[[User, Venue], bool]
type PermissionCallable = CompetitionPermissionCallable | VenuePermissionCallable


class PermissionCheckMixin(MixinProtocol):
    required_permissions: PermissionCallable | list[PermissionCallable] = []
    checked_permissions: list[tuple[str, bool]]

    def get_required_permissions(self) -> list[PermissionCallable]:
        if isinstance(self.required_permissions, list):
            return self.required_permissions
        return [self.required_permissions]

    def get_permission_venue(self) -> Venue | None:
        if hasattr(self, "venue"):
            return getattr(self, "venue")

    def get_permission_competition(self) -> Competition:
        return get_active_competition(self.request)

    def check_access(self, user: User) -> bool:
        self.checked_permissions = []
        allowed = True

        for perm in self.get_required_permissions():
            sig = signature(perm)
            if "venue" in sig.parameters:
                venue = self.get_permission_venue()
                if not venue:
                    raise ImproperlyConfigured(
                        f"{self.__class__.__name__} does not have valid"
                        " permission venue."
                    )
                returned = perm(user, venue)  # type:ignore
            else:
                returned = perm(user, self.get_permission_competition())  # type:ignore

            name = perm.__doc__ or perm.__name__
            self.checked_permissions.append((name, returned))
            allowed = allowed and returned

        return allowed

    def permission_denied_response(self) -> HttpResponse:
        return render(
            self.request,
            "bullet_admin/generic/denied.html",
            {
                "checked_permissions": self.checked_permissions,
                "perm_competition": self.get_permission_competition(),
                "perm_venue": self.get_permission_venue(),
            },
        )

    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        if not request.user.is_authenticated:
            return redirect_to_login(
                self.request.get_full_path(), reverse("badmin:login"), "next"
            )
        elif not self.check_access(request.user):
            return self.permission_denied_response()

        return super().dispatch(request, *args, **kwargs)
