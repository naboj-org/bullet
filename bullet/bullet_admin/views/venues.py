from bullet_admin.access import AdminAccess, CountryAdminAccess, VenueAccess
from bullet_admin.forms.venues import VenueForm
from bullet_admin.utils import get_active_competition
from bullet_admin.views import GenericForm
from competitions.models import Venue
from django.contrib import messages
from django.urls import reverse
from django.views.generic import CreateView, ListView, UpdateView


class VenueListView(AdminAccess, ListView):
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


class VenueUpdateView(VenueAccess, VenueFormMixin, UpdateView):
    form_title = "Edit venue"

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
