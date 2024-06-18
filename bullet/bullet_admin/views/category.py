from competitions.models import Category
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.safestring import mark_safe
from django.views.generic import CreateView, ListView, UpdateView

from bullet_admin.access import BranchAdminAccess
from bullet_admin.forms.category import CategoryForm
from bullet_admin.utils import get_active_competition
from bullet_admin.views import GenericForm, GenericList


class CategoryUpdateView(BranchAdminAccess, GenericForm, UpdateView):
    form_title = "Edit category"
    form_class = CategoryForm

    def get_queryset(self):
        competition = get_active_competition(self.request)
        return Category.objects.filter(competition=competition)

    def get_success_url(self):
        return reverse("badmin:category_list")


class CategoryCreateView(BranchAdminAccess, GenericForm, CreateView):
    form_title = "New category"
    form_class = CategoryForm

    def form_valid(self, form):
        category: Category = form.save(commit=False)
        category.competition = get_active_competition(self.request)
        category.save()

        return redirect("badmin:category_list")


class CategoryListView(GenericList, ListView):
    list_title = "Categories"
    fields = [
        "identifier",
        "order",
        "problems_per_team",
        "max_members_per_team",
        "max_teams_per_school",
    ]
    labels = {
        "identifier": "Category",
        "problems_per_team": "Available problems",
        "max_members_per_team": "Max. team members",
        "max_teams_per_school": mark_safe(
            "Max. teams per school"
            "<span class='ml-1 text-black/70 font-normal'>(2nd round)</span>"
        ),
    }
    create_url = reverse_lazy("badmin:category_create")

    field_templates = {
        "max_teams_per_school": "bullet_admin/categories/max_teams_per_school.html",
    }

    def get_queryset(self):
        return Category.objects.filter(competition=get_active_competition(self.request))

    def get_edit_url(self, category: Category) -> str:
        return reverse("badmin:category_edit", args=[category.pk])
