from urllib.parse import quote

from bullet_admin.utils import get_redirect_url
from django.http import HttpResponseRedirect
from django.urls import resolve, reverse
from django.utils import translation
from django.views import View
from django.views.generic import TemplateView

from countries.logic import country
from countries.logic.detection import get_country_language_from_request
from countries.models import BranchCountry


class CountryDetectView(View):
    redirect_to = "country_selector"

    def get(self, *args):
        detection = get_country_language_from_request(self.request)

        if detection is None:
            url = reverse("country_selector")
            if self.request.path != "/":
                url = f"{url}?next={quote(self.request.get_full_path())}"
        else:
            c, lang = detection
            country.activate(c)
            translation.activate(lang)
            url = f"/{c}/{lang}{self.request.path}"
            resolve(url)

        response = HttpResponseRedirect(redirect_to=url)
        response.headers["Vary"] = "Cookie, Accept-Language"
        response.headers["Cache-Control"] = "no-cache"
        return response


class CountrySelectView(TemplateView):
    template_name = "countries/select.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        countries = []
        for bc in BranchCountry.objects.filter(branch=self.request.BRANCH):
            languages = set(bc.languages) - set(bc.hidden_languages)
            if languages:
                countries.append(
                    {
                        "country": bc.country,
                        "languages": languages,
                    }
                )

        ctx["countries"] = countries
        ctx["redirect"] = get_redirect_url(self.request, "/")
        return ctx
