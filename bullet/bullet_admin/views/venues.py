from bullet_admin.forms.venues import VenueForm
from bullet_admin.mixins import AdminRequiredMixin
from bullet_admin.utils import get_active_competition
from bullet_admin.views import GenericForm
from competitions.models import Venue
from django.contrib import messages
from django.urls import reverse
from django.views.generic import CreateView, ListView, UpdateView


class VenueListView(AdminRequiredMixin, ListView):
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
        ctx["show_new"] = not self.request.user.get_competition_role(
            get_active_competition(self.request)
        ).venues
        ctx["venue_count"] = Venue.objects.for_request(self.request).count()
        return ctx


class VenueFormMixin(GenericForm):
    form_class = VenueForm

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["user"] = self.request.user
        kw["competition"] = get_active_competition(self.request)
        return kw


class VenueUpdateView(AdminRequiredMixin, VenueFormMixin, UpdateView):
    form_title = "Edit venue"

    def get_queryset(self):
        return Venue.objects.for_request(self.request)

    def get_success_url(self):
        messages.success(self.request, "Venue edited succesfully.")
        return reverse("badmin:venue_list")


class VenueCreateView(AdminRequiredMixin, VenueFormMixin, CreateView):
    form_title = "New venue"

    def dispatch(self, request, *args, **kwargs):
        if not self.can_access():
            return self.handle_fail()

        # Restrict venue administrators from creating new venues.
        competition = get_active_competition(self.request)
        if self.request.user.get_competition_role(competition).venues:
            return self.handle_fail()

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, "Venue created succesfully.")
        return reverse("badmin:venue_list")
