from competitions.models import Competition
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.template.loader import get_template
from django.utils import timezone
from django.views.generic import TemplateView
from web.models import Organizer, Partner


class HomepageView(TemplateView):
    template_name = "web/homepage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.branch = self.request.BRANCH

        try:
            context[
                "open_competition"
            ] = Competition.objects.currently_running_registration().get(
                branch=self.branch
            )
            context["registration_open_for"] = (
                context["open_competition"].registration_end - timezone.now()
            )
        except Competition.DoesNotExist:
            pass

        context["partners"] = Partner.objects.filter(branch=self.branch).all()
        context["organizers"] = Organizer.objects.filter(branch=self.branch).all()

        return context


def test(self):
    subject, from_email, to = "guten tag", "naboj@naboj.wtf", "michal.barnas@hostnow.cz"
    text_content = "Das ist eine wichtige Nachricht"
    html_content = get_template("mail/test.html").render()
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    return HttpResponse("417")
