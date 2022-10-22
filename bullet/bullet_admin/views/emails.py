from bullet_admin.forms.emails import EmailCampaignForm
from bullet_admin.mixins import AnyAdminRequiredMixin
from bullet_admin.utils import get_active_competition
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)
from users.models import EmailCampaign


class CampaignListView(AnyAdminRequiredMixin, ListView):
    template_name = "bullet_admin/emails/list.html"

    def get_queryset(self):
        competition = get_active_competition(self.request)
        return EmailCampaign.objects.filter(competition=competition)


class CampaignCreateView(AnyAdminRequiredMixin, CreateView):
    form_class = EmailCampaignForm
    template_name = "bullet_admin/emails/form.html"

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["competition"] = get_active_competition(self.request)
        return kw

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.competition = get_active_competition(self.request)
        obj.save()

        return HttpResponseRedirect(
            reverse("badmin:email_detail", kwargs={"pk": obj.id})
        )


class CampaignUpdateView(AnyAdminRequiredMixin, UpdateView):
    form_class = EmailCampaignForm
    template_name = "bullet_admin/emails/form.html"

    def get_queryset(self):
        return EmailCampaign.objects.filter(
            competition=get_active_competition(self.request)
        )

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["competition"] = get_active_competition(self.request)
        return kw

    def get_success_url(self):
        return reverse("badmin:email_detail", kwargs={"pk": self.object.id})


class CampaignDetailView(AnyAdminRequiredMixin, DetailView):
    template_name = "bullet_admin/emails/detail.html"

    def get_queryset(self):
        return EmailCampaign.objects.filter(
            competition=get_active_competition(self.request)
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["statuses_display"] = [
            EmailCampaign.StatusChoices(x).label for x in self.object.team_statuses
        ]
        ctx["venues_display"] = [
            str(x)
            for x in self.object.team_venues.select_related(
                "category_competition"
            ).all()
        ]
        ctx["team_count"] = self.object.get_teams().count()
        ctx["excluded_count"] = self.object.excluded_teams.count()
        return ctx


class CampaignTeamListView(AnyAdminRequiredMixin, TemplateView):
    template_name = "bullet_admin/emails/teams.html"

    def dispatch(self, request, *args, **kwargs):
        self.campaign = get_object_or_404(
            EmailCampaign,
            competition=get_active_competition(self.request),
            pk=kwargs["pk"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["teams"] = (
            self.campaign.get_teams(ignore_excluded=True)
            .select_related("school", "venue", "venue__category_competition")
            .prefetch_related("contestants")
            .all()
        )
        ctx["excluded_teams"] = set(
            self.campaign.excluded_teams.values_list("id", flat=True)
        )
        return ctx

    def post(self, request, *args, **kwargs):
        teams_to_exclude = request.POST.getlist("excluded")
        self.campaign.excluded_teams.set(teams_to_exclude)

        return HttpResponseRedirect(
            reverse("badmin:email_detail", kwargs={"pk": self.campaign.id})
        )


class CampaignSendTestView(AnyAdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        campaign = get_object_or_404(
            EmailCampaign,
            competition=get_active_competition(self.request),
            pk=kwargs["pk"],
        )
        team = campaign.get_teams().first()
        campaign.send_single(team, request.user.email)

        messages.success(request, "Testing email sent.")
        return HttpResponseRedirect(
            reverse("badmin:email_detail", kwargs={"pk": campaign.id})
        )
