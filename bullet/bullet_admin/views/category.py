from competitions.models import Category
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import CreateView, ListView, UpdateView

from bullet_admin.access import BranchAdminAccess
from bullet_admin.forms.category import CategoryForm
from bullet_admin.utils import get_active_competition
from bullet_admin.views import GenericForm


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


class CategoryListView(ListView):
    template_name = "bullet_admin/categories/list.html"
    paginate_by = 100

    def get_queryset(self):
        competition = get_active_competition(self.request)
        return Category.objects.filter(competition=competition)

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)
        competition = get_active_competition(self.request)
        ctx["category_count"] = Category.objects.filter(competition=competition).count()
        return ctx
