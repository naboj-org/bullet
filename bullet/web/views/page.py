from competitions.models import Competition
from countries.utils import country_reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import translation
from django.views.generic import TemplateView

from web.models import Page


class PageView(TemplateView):
    template_name = "web/page.html"

    def get(self, request, *args, **kwargs):
        if kwargs["slug"] == "_homepage_":
            return HttpResponseRedirect(country_reverse("homepage"))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        competition = Competition.objects.get_current_competition(self.request.BRANCH)
        context["competition"] = competition

        page = get_object_or_404(
            Page,
            branch=self.request.BRANCH,
            language=translation.get_language(),
            countries__contains=[self.request.COUNTRY_CODE.upper()],
            slug=kwargs["slug"],
        )
        context["page"] = page

        current_state = competition.state
        get_state = self.request.GET.get("state", "")
        if self.request.user.is_authenticated and get_state.isnumeric():
            current_state = get_state

        context["page_blocks"] = page.pageblock_set.filter(
            states__contains=[current_state]
        ).all()

        return context
