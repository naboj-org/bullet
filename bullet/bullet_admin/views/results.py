from competitions.models import Category, Venue
from countries.logic.detection import get_country_language_from_request
from django.db.models import Exists, OuterRef
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from django_countries.fields import Country
from problems.models import ResultRow
from users.models import Team
from users.models.organizers import User

from bullet_admin.access import PermissionCheckMixin, is_operator, is_operator_in
from bullet_admin.utils import get_active_competition


class ResultsHomeView(PermissionCheckMixin, TemplateView):
    required_permissions = [is_operator]
    template_name = "bullet_admin/results/select.html"

    def dispatch(self, request, *args, **kwargs):
        self.detection = get_country_language_from_request(self.request)
        if not self.detection:
            return redirect("country_selector")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        assert self.detection
        ctx = super().get_context_data(**kwargs)
        competition = get_active_competition(self.request)
        ctx["competition"] = competition
        ctx["country"], ctx["language"] = self.detection
        ctx["venues"] = Venue.objects.for_competition(competition)
        ctx["my_venues"] = Venue.objects.for_request(self.request)
        ctx["country_categories"] = (
            Venue.objects.for_competition(competition)
            .order_by("category__identifier", "country")
            .distinct("category__identifier", "country")
            .annotate(
                unreviewed=Exists(
                    Venue.objects.for_competition(competition).filter(
                        country=OuterRef("country"),
                        category=OuterRef("category"),
                        is_reviewed=False,
                    )
                )
            )
            .values("category__identifier", "category_id", "country", "unreviewed")
        )
        return ctx


class ResultsAnnouncementView(TemplateView):
    template_name = "bullet_admin/results/announce.html"
    url: str

    def get_team(self, position):
        raise NotImplementedError()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        position = self.request.GET.get("position", "1")
        hidden = "hidden" in self.request.GET
        try:
            position = int(position)
        except ValueError:
            raise Http404()

        ctx["hidden"] = hidden
        ctx["position"] = position

        team = self.get_team(position)
        ctx["team"] = team
        if team:
            ctx["result_row"] = (
                ResultRow.objects.filter(team=team)
                .order_by("-competition_time")
                .first()
            )

        r = reverse(self.url, kwargs=self.kwargs)
        ctx["links"] = {
            "prev": f"{r}?position={position + 1}{'&hidden' if hidden else ''}",
            "hide": f"{r}?position={position}{'&hidden' if not hidden else ''}",
            "next": f"{r}?position={max(1, position - 1)}{'&hidden' if hidden else ''}",
        }
        return ctx


class VenueResultsAnnouncementView(PermissionCheckMixin, ResultsAnnouncementView):
    required_permissions = [is_operator_in]
    url = "badmin:results_announce"

    @cached_property
    def venue(self):
        return get_object_or_404(Venue, id=self.kwargs["venue"])

    def check_custom_permission(self, user: User) -> bool | None:
        """The venue must be reviewed."""
        return self.venue.is_reviewed

    def get_team(self, position):
        return Team.objects.filter(venue=self.venue, rank_venue=position).first()


class CountryResultsAnnouncementView(PermissionCheckMixin, ResultsAnnouncementView):
    required_permissions = [is_operator]
    url = "badmin:results_announce_country"

    @cached_property
    def country(self):
        return Country(self.kwargs["country"])

    @cached_property
    def category(self):
        return get_object_or_404(Category.objects.filter(id=self.kwargs["category"]))

    def check_custom_permission(self, user: User) -> bool:
        """
        You must be a country administrator in the selected country,
        or at least a venue operator of a venue inside the selected country.
        """
        # TODO: The country should be reviewed.
        crole = user.get_competition_role(get_active_competition(self.request))
        if crole.countries:
            return self.country in crole.countries
        if crole.venues:
            return any(filter(lambda v: v.country == self.country, crole.venues))  # type:ignore
        # The fallback here is True -> you don't have neither countries or venues,
        # therefore you must be a higher admin.
        return True

    def get_team(self, position):
        return Team.objects.filter(
            venue__country=self.country,
            venue__category=self.category,
            rank_country=position,
        ).first()
