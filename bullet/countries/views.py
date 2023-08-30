from countries.logic import country
from countries.logic.detection import get_country_language_from_request
from countries.models import BranchCountry
from countries.utils import country_reverse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import translation
from django.views import View
from django.views.generic import TemplateView


class CountryDetectView(View):
    redirect_to = "homepage"

    def get(self, *args):
        detection = get_country_language_from_request(self.request)

        if detection is None:
            url = reverse("country_selector")
        else:
            c, lang = detection
            country.activate(c)
            translation.activate(lang)
            url = country_reverse(self.redirect_to)

        response = HttpResponseRedirect(redirect_to=url)
        response.headers["Vary"] = "Cookie, Accept-Language"
        response.headers["Cache-Control"] = "no-cache"
        return response


class CountrySelectView(TemplateView):
    template_name = "countries/select.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        Countries = []
        for bc in BranchCountry.objects.filter(branch=self.request.BRANCH):
            languages = set(bc.languages) - set(bc.hidden_languages)
            if languages:
                Countries.append(
                    {
                        "country": bc.country,
                        "languages": languages,
                    }
                )

        ctx["countries"] = Countries
        return ctx
