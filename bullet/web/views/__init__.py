from competitions.models import Competition
from django.views.generic import TemplateView
from web.models import Logo


class BranchSpecificTemplateMixin:
    def get_template_names(self):
        previous = super().get_template_names()

        if self.request.BRANCH is None:
            return previous

        templates = []
        for template in previous:
            templates.append(f"{self.request.BRANCH.identifier}/{template}")
            templates.append(template)
        return templates


class HomepageView(BranchSpecificTemplateMixin, TemplateView):
    template_name = "web/homepage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.branch = self.request.BRANCH

        context["competition"] = Competition.objects.get_current_competition(
            self.branch
        )

        context["partners"] = (
            Logo.objects.partners()
            .for_branch_country(self.branch, self.request.COUNTRY_CODE)
            .all()
        )
        context["organizers"] = (
            Logo.objects.organizers()
            .for_branch_country(self.branch, self.request.COUNTRY_CODE)
            .all()
        )

        return context
