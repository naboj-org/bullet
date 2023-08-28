from typing import TYPE_CHECKING

from bullet_admin.mixins import AccessMixin
from bullet_admin.utils import get_active_competition
from django.core.exceptions import ImproperlyConfigured

if TYPE_CHECKING:
    from competitions.models import Competition, Venue
    from users.models import User


def can_access_venue(
    user: "User", venue: "Venue", allow_operator: bool = False
) -> bool:
    """
    Checks whether the given user has access to the given venue.
    This check does not pass for operators unless allow_operator is True.
    """
    if not user.is_authenticated:
        return False

    # Superuser has all permissions
    if user.is_superuser:
        return True

    competition = venue.category_competition.competition
    branch = competition.branch

    # Branch admin can access any venue
    if user.get_branch_role(branch).is_admin:
        return True

    crole = user.get_competition_role(competition)

    if crole.is_operator and not allow_operator:
        return False

    # Country admin can access veunes in his country
    if crole.countries:
        return venue.country in crole.venues

    # Venue admin can access his venues
    if crole.venues:
        return venue in crole.venues

    return False


def is_any_admin(
    user: "User", competition: "Competition", allow_operator: bool = False
) -> bool:
    """
    Checks whether the user is any admin in the competition.
    """
    if not user.is_authenticated:
        return False

    # Superuser has all permissions
    if user.is_superuser:
        return True

    # Branch admin is, obviously an admin
    if user.get_branch_role(competition.branch).is_admin:
        return True

    crole = user.get_competition_role(competition)
    if crole.is_operator and not allow_operator:
        return False

    # Country admin and venue admins are admins, too
    return len(crole.venues) != 0 or len(crole.countries) != 0


def is_country_admin(
    user: "User", competition: "Competition", allow_operator: bool = False
) -> bool:
    """
    Checks whether the user is country admin (or better) in the competition.
    """
    if not user.is_authenticated:
        return False

    # Superuser has all permissions
    if user.is_superuser:
        return True

    # Branch admin is, obviously an admin
    if user.get_branch_role(competition.branch).is_admin:
        return True

    crole = user.get_competition_role(competition)
    if crole.is_operator and not allow_operator:
        return False

    # Country admin and venue admins are admins, too
    return len(crole.countries) != 0


class VenueAccess(AccessMixin):
    """
    Permission check mixin, uses `get_permission_venue` to check users' access to the
    venue.

    `require_unlocked_competition` - whether to require the competition to be unlocked
    to allow access (the competition cannot have results_public)
    `allow_operator` - whether to allow operators to access this view
    """

    require_unlocked_competition = True
    allow_operator = False

    def get_permission_venue(self) -> "Venue":
        raise ImproperlyConfigured(
            "Override get_permission_venue to use VenueAdminMixin."
        )

    def can_access(self):
        venue = self.get_permission_venue()
        if (
            self.require_unlocked_competition
            and venue.category_competition.competition.results_public
        ):
            return False

        return can_access_venue(self.request.user, venue, self.allow_operator)


class AdminAccess(AccessMixin):
    """
    Permission check mixin, uses `get_permission_competition` to check users' access
    to the competition. Allows any admin (branch, venue, country) to acces the view.

    `require_unlocked_competition` - whether to require the competition to be unlocked
    to allow access (the competition cannot have results_public)
    `allow_operator` - whether to allow operators to access this view
    """

    require_unlocked_competition = True
    allow_operator = False

    def get_permission_competition(self) -> "Competition":
        return get_active_competition(self.request)

    def can_access(self):
        competition = self.get_permission_competition()
        if self.require_unlocked_competition and competition.results_public:
            return False

        return is_any_admin(self.request.user, competition, self.allow_operator)


class CountryAdminAccess(AdminAccess):
    """
    Permission check mixin, uses `get_permission_competition` to check users'
    access to the competition. Allows country admin (branch, country) to acces the view.

    `require_unlocked_competition` - whether to require the competition to be unlocked
    to allow access (the competition cannot have results_public)
    `allow_operator` - whether to allow operators to access this view
    """

    def can_access(self):
        competition = self.get_permission_competition()
        if self.require_unlocked_competition and competition.results_public:
            return False

        return is_country_admin(self.request.user, competition, self.allow_operator)
