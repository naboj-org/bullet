from competitions.forms.registration import ContestantForm
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.forms import inlineformset_factory
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.generic import FormView
from users.models import Contestant, Team


class TeamEditView(FormView):
    template_name = "teams/edit.html"

    def get_form_class(self):
        return inlineformset_factory(
            Team, Contestant, form=ContestantForm, validate_max=True
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["team"] = self.team
        ctx["can_be_changed"] = self.can_be_changed
        return ctx

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Team successfully edited.")
        return redirect("team_edit", secret_link=self.team.secret_link)

    def get_form_kwargs(self):
        kw = super(TeamEditView, self).get_form_kwargs()
        kw["instance"] = self.team
        kw["form_kwargs"] = {
            "school_types": self.team.school.types.prefetch_related("grades"),
        }
        return kw

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        form.min_num = 0
        form.max_num = self.category_competition.max_members_per_team
        form.extra = self.category_competition.max_members_per_team - 1
        return form

    def dispatch(self, request, *args, **kwargs):
        self.team = (
            Team.objects.select_related("competition_venue__category_competition")
            .prefetch_related("contestants")
            .get(secret_link=kwargs.pop("secret_link"))
        )
        self.category_competition = self.team.competition_venue.category_competition
        self.can_be_changed = (
            self.category_competition.competition.competition_start > timezone.now()
        )

        if self.team.confirmed_at is None:
            self.team.confirmed_at = timezone.now()
            self.team.save()
            messages.success(request, _("Registration successfully confirmed."))

        return super(TeamEditView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not self.can_be_changed:
            raise PermissionDenied
        return super(TeamEditView, self).post(request, *args, **kwargs)
