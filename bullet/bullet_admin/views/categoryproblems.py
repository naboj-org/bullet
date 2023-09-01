from bullet_admin.access import BranchAdminAccess
from bullet_admin.forms.problem import ProblemsGenerateForm
from bullet_admin.utils import get_active_competition
from bullet_admin.views import GenericForm
from competitions.models import Category
from django.db import transaction
from django.shortcuts import redirect
from django.views.generic import FormView
from problems.models import CategoryProblem, Problem


class ProblemsGenerateView(BranchAdminAccess, GenericForm, FormView):
    form_class = ProblemsGenerateForm
    form_title = "Problem generation"

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["competition"] = get_active_competition(self.request)
        return kw

    @transaction.atomic
    def form_valid(self, form):
        problem_count = form.cleaned_data["problem_count"]
        competition = get_active_competition(self.request)
        print(form.cleaned_data)
        for i in range(problem_count):
            Problem(competition=competition, name=f"{i+1:02d}").save()

        for key in form.cleaned_data.keys():
            if not key.startswith("offset_"):
                continue

            offset = form.cleaned_data[key]
            category = Category.objects.get(competition=competition, identifier=key[7:])
            for i in range(problem_count - offset):
                CategoryProblem(
                    problem=Problem.objects.get(
                        name=f"{i+1+offset:02d}",
                        competition=competition,
                    ),
                    category=category,
                    number=i + 1,
                ).save()

        return redirect("badmin:home")
