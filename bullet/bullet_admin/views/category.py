from django.shortcuts import redirect
from django.views.generic import UpdateView, CreateView, ListView

from bullet_admin.access import BranchAdminAccess, is_branch_admin
from bullet_admin.forms.category import CategoryForm
from bullet_admin.views import GenericForm
from competitions.models import CategoryCompetition, Competition


class CategoryUpdateView(BranchAdminAccess, GenericForm, UpdateView):
    form_title = "Edit Category"
    form_class = CategoryForm

    def get_object(self, queryset=None):
        return CategoryCompetition.objects.filter(id=self.kwargs["pk"]).first()

    def form_valid(self, form):
        category: CategoryCompetition = form.save(commit=False)
        category.save()

        return redirect("badmin:category_list")


class CategoryCreateView(BranchAdminAccess, GenericForm, CreateView):
    form_title = "New Category"
    form_class = CategoryForm

    def form_valid(self, form):
        category: CategoryCompetition = form.save(commit=False)
        category.competition = Competition.objects.get_current_competition(
            self.request.BRANCH
        )
        category.save()

        return redirect("badmin:category_list")


class CategoryListView(ListView):
    template_name = "bullet_admin/categories/list.html"
    paginate_by = 100

    def get_queryset(self):
        competition = Competition.objects.get_current_competition(self.request.BRANCH)
        return CategoryCompetition.objects.filter(competition=competition)

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)
        competition = Competition.objects.get_current_competition(self.request.BRANCH)
        ctx["category_count"] = CategoryCompetition.objects.filter(
            competition=competition
        ).count()
        ctx["is_branch_admin"] = is_branch_admin(self.request.user, self.request.BRANCH)
        return ctx
