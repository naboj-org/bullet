from bullet_admin.access import BranchAdminAccess
from bullet_admin.forms.problem import CategoryProblemForm
from bullet_admin.views import GenericForm
from competitions.models import Category, Competition
from django.shortcuts import redirect
from django.views.generic import FormView
from problems.models import CategoryProblem, Problem


class CategoryProblemFormMixin(GenericForm):
    form_class = CategoryProblemForm

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["branch"] = self.request.BRANCH
        return kw


class CategoryProblemEdit(BranchAdminAccess, CategoryProblemFormMixin, FormView):
    form_class = CategoryProblemForm
    form_title = "Problem Generation"

    def get_object(self, queryset=None):
        competition = Competition.objects.get_current_competition(self.request.BRANCH)
        categories = Category.objects.filter(competition=competition)
        competitionProblems = CategoryProblem.objects.filter(
            category__competition=competition
        )
        return {
            "problem_count": competitionProblems.count(),
            "offsets": [
                competitionProblems.filter(category=category).order_by("number").first()
                for category in categories
            ],
        }

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["branch"] = self.request.BRANCH
        return kw

    def form_valid(self, form):
        problem_count = form.cleaned_data["problem_count"]
        competition = Competition.objects.get_current_competition(self.request.BRANCH)
        print(form.cleaned_data)
        for i in range(problem_count):
            Problem(
                competition=competition, name="Problem {number}".format(number=i)
            ).save()

        for offset in form.cleaned_data.keys():
            if not offset.startswith("offset_"):
                continue
            starting_problem = form.cleaned_data[offset]
            category = Category.objects.filter(identifier=offset[7:]).first()
            for i in range(starting_problem, problem_count):
                CategoryProblem(
                    problem=Problem.objects.filter(
                        name="Problem {number}".format(number=i)
                    ).first(),
                    category=category,
                    number=i + 1,
                ).save()

        return redirect("badmin:home")
