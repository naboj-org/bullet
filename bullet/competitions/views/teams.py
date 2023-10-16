from collections import defaultdict

from competitions.forms.registration import ContestantForm
from competitions.models import Category, Competition, Venue
from countries.utils import country_reverse
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import QuerySet
from django.forms import inlineformset_factory
from django.http import (
    FileResponse,
    Http404,
    HttpResponseForbidden,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import DeleteView, FormView, TemplateView
from documents.generators.certificate import certificate_for_team
from documents.models import SelfServeCertificate
from users.emails.admin import UnregisteredTeam, send_team_unregistered
from users.logic import (
    add_team_to_competition,
    get_venue_waiting_list,
    get_venues_waiting_list,
)
from users.models import Contestant, Team


class TeamEditView(FormView):
    template_name = "teams/edit.html"

    def get_form_class(self):
        return inlineformset_factory(
            Team, Contestant, form=ContestantForm, validate_max=True
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["team"] = self.team
        ctx["can_be_changed"] = self.can_be_changed
        ctx["show_certificate"] = (
            self.category.competition.results_public
            and SelfServeCertificate.objects.filter(venue=self.team.venue).exists()
        )
        return ctx

    def form_valid(self, form):
        form.save()
        if "consent_photos" in self.request.POST:
            self.team.consent_photos = True
            self.team.save()
        messages.success(self.request, _("Team successfully edited."))
        return HttpResponseRedirect(
            country_reverse("team_edit", kwargs={"secret_link": self.team.secret_link})
        )

    def get_form_kwargs(self):
        kw = super(TeamEditView, self).get_form_kwargs()
        kw["instance"] = self.team
        kw["form_kwargs"] = {
            "school_types": self.team.school.types.prefetch_related("grades"),
            "category": self.category,
        }
        return kw

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        form.min_num = 0
        form.max_num = self.category.max_members_per_team
        form.extra = self.category.max_members_per_team
        return form

    def dispatch(self, request, *args, **kwargs):
        self.team = (
            Team.objects.select_related("venue__category")
            .prefetch_related("contestants", "contestants__grade")
            .filter(secret_link=kwargs.pop("secret_link"))
            .first()
        )
        if not self.team:
            raise Http404()

        self.category = self.team.venue.category
        if not self.team.venue.registration_flow.can_edit(self.team):
            self.can_be_changed = False
        else:
            self.can_be_changed = (
                self.category.competition.competition_start > timezone.now()
                and not self.team.is_checked_in
            )

        if self.team.confirmed_at is None:
            self.team.confirmed_at = timezone.now()
            add_team_to_competition(self.team)
            self.team.save()
            messages.success(request, _("Registration successfully confirmed."))

        return super(TeamEditView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not self.can_be_changed:
            raise PermissionDenied
        return super(TeamEditView, self).post(request, *args, **kwargs)


class TeamListView(TemplateView):
    template_name = "teams/list.html"

    def get_teams(self, venues) -> QuerySet[Team]:
        return (
            Team.objects.competing()
            .filter(venue__in=venues)
            .prefetch_related("contestants", "contestants__grade")
            .select_related("school")
        )

    def get_countries(self):
        return (
            Venue.objects.filter(category__competition=self.competition)
            .order_by("country")
            .distinct("country")
            .values_list("country", flat=True)
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data()
        self.competition: Competition = Competition.objects.get_current_competition(
            self.request.BRANCH
        )

        country: str = self.request.GET.get(
            "country", self.request.COUNTRY_CODE
        ).upper()
        venues: QuerySet[Venue] = (
            Venue.objects.for_competition(self.competition)
            .filter(country=country)
            .all()
        )
        teams: QuerySet[Team] = self.get_teams(venues).all()

        venue_teams: dict[int, list[Team]] = defaultdict(lambda: [])
        for team in teams:
            venue_teams[team.venue_id].append(team)

        ctx["venues"] = [{"venue": v, "teams": venue_teams[v.id]} for v in venues]
        ctx["country"] = country
        ctx["countries"] = self.get_countries()
        return ctx


class WaitingListView(TeamListView):
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["is_waitinglist"] = True
        return ctx

    def get_teams(self, venues) -> QuerySet[Team]:
        category_venues = {}
        for venue in venues:
            if venue.category_id not in category_venues:
                category_venues[venue.category_id] = [venue]
            else:
                category_venues[venue.category_id].append(venue)

        qs = Team.objects.none()
        for venue_groups in category_venues.values():
            wl = (
                get_venues_waiting_list(venue_groups)
                .prefetch_related("contestants", "contestants__grade")
                .select_related("school")
            )
            qs = qs.union(wl)

        return qs


class TeamDeleteView(DeleteView):
    template_name = "teams/delete.html"

    def get_object(self, queryset=None):
        return get_object_or_404(Team, secret_link=self.kwargs["secret_link"])

    @transaction.atomic
    def form_valid(self, form):
        team: Team = self.object
        category: Category = team.venue.category
        competition: Competition = category.competition
        if team.is_checked_in or competition.competition_start <= timezone.now():
            return HttpResponseForbidden()

        unregistered_team = UnregisteredTeam(
            team.id_display,
            team.code,
            team.venue,
            team.display_name,
            team.contestants_names,
        )
        self.object.delete()

        if competition.is_registration_open and not team.is_waiting:
            waiting_list = get_venue_waiting_list(team.venue).first()
            if (
                waiting_list
                and waiting_list.from_school
                <= category.max_teams_per_school_at(timezone.now())
            ):
                waiting_list.to_competition()
                waiting_list.save()

        if competition.registration_end <= timezone.now():
            send_team_unregistered.delay(unregistered_team)

        messages.success(self.request, _("Team was unregistered."))
        return HttpResponseRedirect(country_reverse("homepage"))


class TeamCertificateView(View):
    def dispatch(self, request, *args, **kwargs):
        self.team = get_object_or_404(Team, secret_link=self.kwargs["secret_link"])
        if not self.team.venue.category.competition.results_public:
            raise PermissionDenied()

        self_serve = SelfServeCertificate.objects.filter(venue=self.team.venue).first()
        if not self_serve:
            raise Http404()
        self.template = self_serve.template

        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = certificate_for_team(self.template, self.team)
        return FileResponse(
            data, as_attachment=True, filename=f"certificate-{self.team.code}.pdf"
        )
