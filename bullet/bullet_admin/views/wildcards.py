from competitions.models import Wildcard
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, ListView

from bullet_admin.access import CountryAdminAccess
from bullet_admin.forms.teams import WildcardForm
from bullet_admin.utils import get_active_competition
from bullet_admin.views import GenericForm


class WildcardQuerySetMixin:
    def get_queryset(self):
        competition = get_active_competition(self.request)
        qs = Wildcard.objects.filter(competition=competition).order_by(
            "category__order", "school__country", "school__name"
        )
        return qs


class WildcardListView(CountryAdminAccess, WildcardQuerySetMixin, ListView):
    template_name = "bullet_admin/wildcards/list.html"


class WildcardCreateView(
    CountryAdminAccess, WildcardQuerySetMixin, GenericForm, CreateView
):
    form_title = "New wildcard"
    form_class = WildcardForm

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["competition"] = get_active_competition(self.request)
        return kw

    def get_success_url(self):
        return reverse("badmin:wildcard_list")


class WildcardDeleteView(CountryAdminAccess, WildcardQuerySetMixin, DeleteView):
    template_name = "bullet_admin/wildcards/delete.html"

    def get_success_url(self):
        return reverse("badmin:wildcard_list")
