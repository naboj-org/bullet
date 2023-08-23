from bullet_admin.forms.venues import VenueForm
from bullet_admin.mixins import AdminRequiredMixin
from bullet_admin.utils import can_access_venue, get_active_competition
from competitions.models import Venue
from django.contrib import messages
from django.urls import reverse
from django.views.generic import CreateView, ListView, UpdateView


class VenueObjectMixin:
    def get_queryset(self):
        return Venue.objects.for_request(self.request)


class VenueListView(AdminRequiredMixin, VenueObjectMixin, ListView):
    template_name = "bullet_admin/venues/list.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)
        ctx["show_new"] = not self.request.user.get_competition_role(
            get_active_competition(self.request)
        ).venues
        return ctx


class VenueUpdateView(AdminRequiredMixin, VenueObjectMixin, UpdateView):
    template_name = "bullet_admin/venues/form.html"
    form_class = VenueForm

    def get_object(self, queryset=None):
        if not hasattr(self, "_object"):
            self._object = super().get_object(queryset)
        return self._object

    def dispatch(self, request, *args, **kwargs):
        if not self.can_access():
            return self.handle_fail()

        if not can_access_venue(request, self.get_object()):
            return self.handle_fail()

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["user"] = self.request.user
        kw["competition"] = get_active_competition(self.request)
        return kw

    def get_success_url(self):
        messages.success(self.request, "Venue edited succesfully.")
        return reverse("badmin:venue_list")


class VenueCreateView(AdminRequiredMixin, CreateView):
    template_name = "bullet_admin/venues/form.html"
    form_class = VenueForm

    def dispatch(self, request, *args, **kwargs):
        if not self.can_access():
            return self.handle_fail()

        # Restrict venue administrators from creating new venues.
        competition = get_active_competition(self.request)
        if self.request.user.get_competition_role(competition).venues:
            return self.handle_fail()

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["user"] = self.request.user
        kw["competition"] = get_active_competition(self.request)
        return kw

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["create"] = True
        return ctx

    def get_success_url(self):
        messages.success(self.request, "Venue created succesfully.")
        return reverse("badmin:venue_list")
