from competitions.models import Venue
from django.contrib import messages
from django.forms import Form
from django.http import FileResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.functional import cached_property
from django.views import View
from django.views.generic import CreateView, DetailView, FormView, ListView, UpdateView
from documents.generators.certificate import certificates_for_venue
from documents.generators.team_list import team_list
from users.emails.teams import send_to_competition_email
from users.logic import get_venue_waiting_list
from users.models import Team

from bullet_admin.access import AdminAccess, CountryAdminAccess, VenueAccess
from bullet_admin.forms.documents import CertificateForm
from bullet_admin.forms.venues import VenueForm
from bullet_admin.mixins import AdminRequiredMixin
from bullet_admin.utils import get_active_competition
from bullet_admin.views import GenericForm


class VenueListView(AdminAccess, ListView):
    require_unlocked_competition = False
    template_name = "bullet_admin/venues/list.html"
    paginate_by = 100

    def get_queryset(self):
        # For whatever reason, when you annotate the queryset, it loses
        # the default ordering...
        return (
            Venue.objects.for_request(self.request).annotate_teamcount().natural_order()
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)
        ctx["venue_count"] = Venue.objects.for_request(self.request).count()
        return ctx


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
        data = certificates_for_venue(
            self.venue,
            form.cleaned_data["template"],
            form.cleaned_data["count"],
            form.cleaned_data["empty"],
        )
        return FileResponse(data, as_attachment=True, filename="certificates.pdf")


class TeamListView(VenueMixin, GenericForm, FormView):
    require_unlocked_competition = False
    form_class = Form

    def form_valid(self, form):
        venue = self.venue
        data = team_list(
            Team.objects.competing().filter(venue=venue, number__isnull=False),
            f"Team list: {venue.name}",
        )
        return FileResponse(data, as_attachment=True, filename="team_list.pdf")


class WaitingListView(AdminRequiredMixin, VenueMixin, ListView):
    require_unlocked_competition = False
    template_name = "bullet_admin/venues/waiting_list.html"

    def get_queryset(self):
        return get_venue_waiting_list(self.venue)


class WaitingListAutomoveView(AdminRequiredMixin, VenueMixin, View):
    def post(self, request, *args, **kwargs):
        team_count = self.venue.remaining_capacity
        waiting_list = get_venue_waiting_list(self.venue)[:team_count]

        for team in waiting_list:
            team.to_competition()
            team.save()

            send_to_competition_email.delay(team.id)

        return HttpResponseRedirect(self.get_redirect_url())

    def get_redirect_url(self):
        return reverse("badmin:waiting_list", kwargs={"pk": self.venue.id})
