import random
import string
from typing import Tuple

from competitions.models import CategoryCompetition, Competition, CompetitionSite
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import F, QuerySet
from django.forms import ModelForm, inlineformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.template.loader import get_template
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView
from django_hosts import reverse
from users.models import Participant, Team
from web.forms import RegistrationForm
from web.views import BranchViewMixin


class RegistrationView(BranchViewMixin, FormView):
    template_name = "web/registration.html"
    form_class = RegistrationForm

    def get_success_url(self):
        return reverse("homepage", host=self.branch.label.lower())

    def get_competition_model_instances(
        self,
    ) -> Tuple[CategoryCompetition, QuerySet[CompetitionSite]]:
        try:
            competition = Competition.objects.currently_running_registration().get(
                branch=self.branch
            )
        except Competition.DoesNotExist:
            raise ValueError(
                f"No {self.branch} competition has an open registration now"
            )

        try:
            category_competition = CategoryCompetition.objects.get(
                competition=competition, category=self.kwargs["category"]
            )
        except CategoryCompetition.DoesNotExist:
            raise ValueError(
                f'{self.kwargs["category"]} category cannot compete in {competition}'
            )

        competition_sites = CompetitionSite.objects.with_occupancy().filter(
            category_competition=category_competition, occupancy__lt=F("capacity")
        )

        if competition_sites.count() == 0:
            raise ValueError(f"All competition sites have reached full occupancy")

        return category_competition, competition_sites

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["available_sites"] = self.kwargs["sites"]
        kwargs["category_competition"] = self.kwargs["category_competition"]
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["formset"] = self.get_formset()
        return ctx

    def get_formset(self):
        category_competition: CategoryCompetition = self.kwargs["category_competition"]
        return inlineformset_factory(
            Team,
            Participant,
            min_num=0,
            max_num=category_competition.max_members_per_team,
            extra=category_competition.max_members_per_team - 1,
            fields=("full_name", "graduation_year", "birth_year"),
        )(**self.get_formset_kwargs())

    def get_formset_kwargs(self):
        kwargs = {}
        if self.request.method in ("POST", "PUT"):
            kwargs.update(
                {
                    "data": self.request.POST,
                    "files": self.request.FILES,
                }
            )
        return kwargs

    @transaction.atomic
    def dispatch(self, request, *args, **kwargs):
        try:
            category_competition, sites = self.get_competition_model_instances()
            self.kwargs.update(
                {"category_competition": category_competition, "sites": sites}
            )
        except ValueError as e:
            messages.error(request, str(e))
            return HttpResponseRedirect(
                reverse("homepage", host=self.branch.label.lower())
            )

        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        formset = self.get_formset()
        if form.is_valid() and formset.is_valid():
            return self.forms_valid(form, formset)
        else:
            return self.form_invalid(form)

    def forms_valid(self, form, formset):
        team = form.save(commit=False)
        team.is_official = True
        team.secret_link = "".join(
            random.choices(string.ascii_letters + string.digits, k=48)
        )
        team.save()

        form: ModelForm
        participants = formset.save(commit=False)
        for participant in participants:
            participant.team = team
            participant.save()

        send_mail(
            _("Confirm team registration for Náboj"),
            get_template("users/email/registration_secret_link.html").render(
                {
                    "host": self.branch.label.lower(),
                    "team": team,
                    "participants": participants,
                }
            ),
            team.competition_site.email_alias or settings.EMAIL_HOST_USER,
            [team.contact_email],
        )
        return super().form_valid(form)


class RegistrationConfirmView(BranchViewMixin, TemplateView):
    template_name = "web/registration_confirm.html"

    @transaction.atomic
    def get(self, request, *args, **kwargs):
        secret_link = kwargs.pop("secret_link")

        try:
            team = Team.objects.select_related(
                "competition_site__category_competition__competition"
            ).get(secret_link=secret_link)
            if team.confirmed_at is not None:
                return redirect("team_edit", secret_link=secret_link)
            else:
                team.confirmed_at = timezone.now()
                team.save(update_fields=("confirmed_at",))
                error = None

        except Team.DoesNotExist:
            error = _("Confirmation link is invalid")

        # TODO forbid confirmation if the registration is not running/capacity has been filled
        context = self.get_context_data(**kwargs)
        context["error"] = error

        return self.render_to_response(context)
