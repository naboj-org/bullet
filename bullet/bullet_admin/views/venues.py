from pathlib import Path

from competitions.models import Venue
from django.contrib import messages
from django.core.files.storage import default_storage
from django.forms import Form
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import (
    CreateView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
)
from documents.generators.certificate import certificates_for_venue
from documents.generators.team_list import team_list
from documents.generators.tearoff import (
    TearoffGenerator,
    TearoffRequirementMissingError,
)
from documents.models import TexJob
from problems.logic.results import (
    get_venue_results,
    save_country_ranks,
    save_venue_ranks,
)
from problems.models import Problem
from users.logic import get_venue_waiting_list, move_eligible_teams
from users.models import Team

from bullet_admin.access import (
    AdminAccess,
    CountryAdminAccess,
    VenueAccess,
    is_country_admin,
)
from bullet_admin.forms.documents import CertificateForm, TearoffForm
from bullet_admin.forms.venues import TeamListForm, VenueForm
from bullet_admin.mixins import AdminRequiredMixin, AuthedHttpRequest, RedirectBackMixin
from bullet_admin.utils import get_active_competition
from bullet_admin.views import GenericForm
from bullet_admin.views.generic.links import Link, NewLink, ViewIcon
from bullet_admin.views.generic.list import GenericList


class VenueListView(AdminAccess, GenericList, ListView):
    request: AuthedHttpRequest  # type: ignore
    require_unlocked_competition = False

    table_fields = ["name", "category", "team_count", "capacity", "local_start"]
    table_labels = {
        "name": "Venue",
        "team_count": "Registered teams",
    }
    table_field_templates = {
        "name": "bullet_admin/venues/field__venue.html",
    }

    def get_category_content(self, obj):
        return obj.category.identifier.title()

    def get_list_links(self) -> list[Link]:
        links = []

        competition = get_active_competition(self.request)
        if is_country_admin(self.request.user, competition):
            links.append(NewLink("venue", reverse("badmin:venue_create")))

        return links

    def get_queryset(self):
        # For whatever reason, when you annotate the queryset, it loses
        # the default ordering...
        return (
            Venue.objects.for_request(self.request).annotate_teamcount().natural_order()
        )

    def get_row_links(self, obj) -> list[Link]:
        return [ViewIcon(reverse("badmin:venue_detail", kwargs={"pk": obj.id}))]


class VenueFormMixin(GenericForm):
    form_class = VenueForm

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["user"] = self.request.user
        kw["competition"] = get_active_competition(self.request)
        return kw


class VenueDetailView(VenueAccess, DetailView):
    require_unlocked_competition = False
    template_name = "bullet_admin/venues/detail.html"

    def get_permission_venue(self) -> Venue:
        return self.get_object()

    def get_queryset(self):
        return Venue.objects.for_request(self.request)


class VenueUpdateView(VenueAccess, VenueFormMixin, UpdateView):
    form_title = "Edit venue"
    template_name = "bullet_admin/venues/form.html"

    def get_permission_venue(self) -> Venue:
        return self.get_object()

    def get_queryset(self):
        return Venue.objects.for_request(self.request)

    def get_success_url(self):
        messages.success(self.request, "Venue edited succesfully.")
        return reverse("badmin:venue_list")


class VenueCreateView(CountryAdminAccess, VenueFormMixin, CreateView):
    form_title = "New venue"

    def get_success_url(self):
        messages.success(self.request, "Venue created succesfully.")
        return reverse("badmin:venue_list")


class VenueMixin(VenueAccess):
    template_name = "bullet_admin/venues/form.html"

    def get_permission_venue(self) -> "Venue":
        return self.venue

    @cached_property
    def venue(self):
        return get_object_or_404(
            Venue.objects.for_request(self.request), id=self.kwargs["pk"]
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["venue"] = self.venue
        return ctx


class CertificateView(VenueMixin, GenericForm, FormView):
    require_unlocked_competition = False
    form_class = CertificateForm

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["competition"] = get_active_competition(self.request)
        return kw

    def form_valid(self, form):
        if template := form.cleaned_data.get("tex_template"):
            if self.venue.is_reviewed:
                teams = (
                    Team.objects.competing()
                    .filter(venue=self.venue)
                    .order_by("rank_venue")
                    .select_related(
                        "school",
                        "venue",
                        "venue__category",
                    )
                    .prefetch_related("contestants", "contestants__grade")
                )
                if count := form.cleaned_data.get("count"):
                    teams = teams.filter(rank_venue__lte=count)
            else:
                if count := form.cleaned_data.get("count"):
                    results = get_venue_results(self.venue)
                    results = results[:count]

                    teams = []
                    for rank_i, row in enumerate(results):
                        team = row.team
                        team.rank_venue = rank_i + 1
                        teams.append(team)
                else:
                    teams = (
                        Team.objects.competing()
                        .filter(venue=self.venue)
                        .select_related(
                            "school",
                            "venue",
                            "venue__category",
                        )
                        .prefetch_related("contestants", "contestants__grade")
                    )

            job = TexJob.objects.create(
                template=template,
                creator=self.request.user,
                context={"teams": [t.to_export() for t in teams]},
            )
            job.render()
            return redirect("badmin:tex_job_detail", pk=job.id)

        data = certificates_for_venue(
            self.venue,
            form.cleaned_data["template"],
            form.cleaned_data["count"],
            form.cleaned_data["empty"],
        )
        return FileResponse(data, as_attachment=True, filename="certificates.pdf")


class TeamListView(VenueMixin, GenericForm, FormView):
    require_unlocked_competition = False
    form_class = TeamListForm

    def form_valid(self, form):
        venue = self.venue
        data = team_list(
            Team.objects.competing().filter(venue=venue, number__isnull=False),
            f"Team list: {venue.name}",
            **form.cleaned_data,
        )
        return FileResponse(data, as_attachment=True, filename="team_list.pdf")


class WaitingListView(AdminRequiredMixin, VenueMixin, ListView):
    require_unlocked_competition = False
    template_name = "bullet_admin/venues/waiting_list.html"

    def get_queryset(self):
        return get_venue_waiting_list(self.venue)


class WaitingListAutomoveView(AdminRequiredMixin, VenueMixin, GenericForm, FormView):
    form_class = Form
    form_title = "Move waiting lists automatically"
    form_submit_label = "Move automatically"
    form_submit_color = "green"
    form_submit_icon = "mdi:fast-forward"
    template_name = "bullet_admin/venues/waiting_list_automove.html"

    def form_valid(self, form):
        move_eligible_teams(self.venue)
        return HttpResponseRedirect(self.get_redirect_url())

    def get_redirect_url(self):
        return reverse("badmin:waiting_list", kwargs={"pk": self.venue.id})


class TearoffView(VenueMixin, GenericForm, FormView):
    form_class = TearoffForm
    form_multipart = True
    template_name = "bullet_admin/venues/tearoffs.html"

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        competition = get_active_competition(self.request)
        problem_count = Problem.objects.filter(competition=competition).count()

        kw["problems"] = problem_count
        kw["venue"] = self.venue
        kw["first_problem"] = self.venue.category.first_problem
        return kw

    def form_valid(self, form):
        competition = self.venue.category.competition

        try:
            tearoff_dir = Path(
                default_storage.path(competition.secret_dir / "tearoffs")
            )
            t = TearoffGenerator(tearoff_dir, form.cleaned_data["backup_team_language"])
        except TearoffRequirementMissingError as e:
            return HttpResponse(str(e), status=500)

        teams = list(
            Team.objects.competing()
            .filter(venue=self.venue, number__isnull=False)
            .all()
        )

        for i in range(form.cleaned_data["backup_teams"]):
            teams.append(
                Team(
                    venue=self.venue,
                    language=form.cleaned_data["backup_team_language"],
                    name="???",
                    number=999 - i,
                )
            )

        try:
            data = t.generate_pdf(
                teams,
                form.cleaned_data["first_problem"],
                form._problem_count,
                form.cleaned_data["ordering"],
                form.cleaned_data["include_qr_codes"],
            )
            return FileResponse(data, filename="tearoffs.pdf")
        except TearoffRequirementMissingError as e:
            return HttpResponse(str(e), status=500)


class FinishReviewView(VenueMixin, RedirectBackMixin, GenericForm, FormView):
    form_class = Form
    form_title = "Finish venue review"
    form_submit_color = "green"
    form_submit_label = "Finish review"
    form_submit_icon = "mdi:check"
    template_name = "bullet_admin/venues/finish_review.html"

    def get_default_success_url(self):
        return reverse("badmin:venue_detail", kwargs={"pk": self.venue.id})

    def form_valid(self, form):
        if self.venue.has_unreviewed_teams:
            messages.error(self.request, "This venue has unreviewed teams.")
            return redirect("badmin:venue_finish_review", self.venue.id)

        self.venue.is_reviewed = True
        self.venue.save()

        save_venue_ranks.delay(self.venue.id)

        unreviewed_venue = Venue.objects.filter(
            category=self.venue.category, country=self.venue.country, is_reviewed=False
        ).exists()
        if not unreviewed_venue:
            save_country_ranks.delay(self.venue.category.id, self.venue.country)

        return super().form_valid(form)
