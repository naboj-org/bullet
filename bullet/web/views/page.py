from django.shortcuts import get_object_or_404
from django.utils import translation
from django.views.generic import TemplateView

from web.models import Page


class PageView(TemplateView):
    template_name = "web/page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["page"] = get_object_or_404(
            Page,
            branch=self.request.BRANCH,
            language=translation.get_language(),
            countries__contains=[self.request.COUNTRY_CODE.upper()],
            slug=kwargs["slug"],
        )

        return context
