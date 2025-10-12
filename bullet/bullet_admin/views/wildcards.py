from competitions.models import Wildcard
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView

from bullet_admin.access_v2 import (
    PermissionCheckMixin,
    is_competition_unlocked,
    is_country_admin,
)
from bullet_admin.forms.teams import WildcardForm
from bullet_admin.utils import get_active_competition
from bullet_admin.views import GenericForm
from bullet_admin.views.generic.links import DeleteIcon, Link, NewLink
from bullet_admin.views.generic.list import GenericList


class WildcardViewMixin(PermissionCheckMixin):
    required_permissions = [is_country_admin, is_competition_unlocked]

    def get_queryset(self):
        competition = get_active_competition(self.request)
        qs = Wildcard.objects.filter(competition=competition).order_by(
            "category__order", "school__country", "school__name"
        )
        return qs


class WildcardListView(WildcardViewMixin, GenericList, ListView):
    list_subtitle = (
        "Wildcards allow schools to register additional teams during "
        "the first round of the registration."
    )

    list_links = [NewLink("wildcard", reverse_lazy("badmin:wildcard_create"))]
    table_fields = ["category", "school", "note"]

    def get_category_content(self, obj):
        if not obj.category:
            return "(none)"
        return obj.category.identifier.title()

    def get_row_links(self, obj) -> list[Link]:
        return [DeleteIcon(reverse("badmin:wildcard_delete", args=[obj.pk]))]


class WildcardCreateView(WildcardViewMixin, GenericForm, CreateView):
    form_title = "New wildcard"
    form_class = WildcardForm

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["competition"] = get_active_competition(self.request)
        return kw

    def get_success_url(self):
        return reverse("badmin:wildcard_list")


class WildcardDeleteView(WildcardViewMixin, DeleteView):
    template_name = "bullet_admin/wildcards/delete.html"

    def get_success_url(self):
        return reverse("badmin:wildcard_list")
