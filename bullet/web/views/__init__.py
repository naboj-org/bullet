from competitions.models import Competition
from django.shortcuts import render
from django.utils import translation
from django.views.generic import RedirectView, TemplateView

from web.models import Logo, Page


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

        context["competition"] = (
            competition
        ) = Competition.objects.get_current_competition(self.branch)

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

        page = Page.objects.filter(
            branch=self.request.BRANCH,
            language=translation.get_language(),
            countries__contains=[self.request.COUNTRY_CODE.upper()],
            slug="_homepage_",
        ).first()
        if page:
            context["page_blocks"] = page.pageblock_set.filter(
                states__contains=[competition.state]
            ).all()

        return context


class AdminRedirectView(RedirectView):
    url = "/admin/"


def error_404_view(request, *args, **kwargs):
    response = render(request, "web/404.html")
    response.status_code = 404
    return response
