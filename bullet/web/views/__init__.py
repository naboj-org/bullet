from competitions.models import Competition
from django.shortcuts import render
from django.utils import translation
from django.views.generic import RedirectView, TemplateView

from web.models import Page


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

        page = Page.objects.filter(
            branch=self.request.BRANCH,
            language=translation.get_language(),
            countries__contains=[self.request.COUNTRY_CODE.upper()],
            slug="_homepage_",
        ).first()
        if page:
            current_state = competition.state
            get_state = self.request.GET.get("state", "")
            if self.request.user.is_authenticated and get_state.isnumeric():
                current_state = get_state

            context["page_blocks"] = page.pageblock_set.filter(
                states__contains=[current_state]
            ).all()

        return context


class AdminRedirectView(RedirectView):
    url = "/admin/"


def error_404_view(request, *args, **kwargs):
    response = render(request, "web/404.html")
    response.status_code = 404
    return response
