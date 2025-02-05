from competitions.models import Wildcard
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView

from bullet_admin.access import CountryAdminAccess
from bullet_admin.forms.teams import WildcardForm
from bullet_admin.utils import get_active_competition
from bullet_admin.views import GenericForm
from bullet_admin.views.generic.links import DeleteIcon, Link, NewLink
from bullet_admin.views.generic.list import GenericList


class WildcardQuerySetMixin:
    def get_queryset(self):
        competition = get_active_competition(self.request)
        qs = Wildcard.objects.filter(competition=competition).order_by(
            "category__order", "school__country", "school__name"
        )
        return qs


class WildcardListView(
    CountryAdminAccess, WildcardQuerySetMixin, GenericList, ListView
):
    list_subtitle = (
        "Wildcards allow schools to register additional teams during "
        "the first round of the registration."
    )

    list_links = [NewLink("wildcard", reverse_lazy("badmin:wildcard_create"))]
    table_fields = ["category", "school", "note"]

    def get_category_content(self, object):
        if not object.category:
            return "(none)"
        return object.category.identifier.title()

    def get_row_links(self, object) -> list[Link]:
        return [DeleteIcon(reverse("badmin:wildcard_delete", args=[object.pk]))]


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
