from competitions.branches import Branch
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)
from users.models import EmailCampaign, TeamStatus, User

from bullet_admin.forms.emails import EmailCampaignForm
from bullet_admin.mixins import AdminRequiredMixin
from bullet_admin.utils import get_active_competition


def can_edit_campaign(request, campaign: EmailCampaign):
    user: User = request.user
    branch: Branch = request.BRANCH
    if user.get_branch_role(branch).is_admin:
        return True

    # Only branch admin can edit global emails
    if not campaign.team_countries and not campaign.team_venues.exists():
        return False

    competition = get_active_competition(request)
    crole = user.get_competition_role(competition)

    # Country admin can only edit campaigns from his countries
    if crole.countries:
        if not set(crole.countries).issuperset(set(campaign.team_countries)):
            return False

        if not set(crole.countries).issuperset(
            set(campaign.team_venues.values_list("country", flat=True))
        ):
            return False

    # Venue admin can only edit campaigns targeting his venues
    venues = crole.venues
    if venues:
        if campaign.team_countries:
            return False
        if not set(venues).issuperset(set(campaign.team_venues.all())):
            return False

    return True


class CampaignListView(AdminRequiredMixin, ListView):
    template_name = "bullet_admin/emails/list.html"

    def get_queryset(self):
        competition = get_active_competition(self.request)
        return EmailCampaign.objects.filter(competition=competition)


class CampaignCreateView(AdminRequiredMixin, CreateView):
    form_class = EmailCampaignForm
    template_name = "bullet_admin/emails/form.html"

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["competition"] = get_active_competition(self.request)
        kw["user"] = self.request.user
        return kw

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.competition = get_active_competition(self.request)
        obj.save()
        form.save_m2m()

        return HttpResponseRedirect(
            reverse("badmin:email_detail", kwargs={"pk": obj.id})
        )


class CampaignUpdateView(AdminRequiredMixin, UpdateView):
    form_class = EmailCampaignForm
    template_name = "bullet_admin/emails/form.html"

    def get_queryset(self):
        return EmailCampaign.objects.filter(
            competition=get_active_competition(self.request)
        )

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not can_edit_campaign(self.request, obj):
            raise PermissionDenied()
        return obj

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["competition"] = get_active_competition(self.request)
        kw["user"] = self.request.user
        return kw

    def get_success_url(self):
        return reverse("badmin:email_detail", kwargs={"pk": self.object.id})


class CampaignDetailView(AdminRequiredMixin, DetailView):
    template_name = "bullet_admin/emails/detail.html"

    def get_queryset(self):
        return EmailCampaign.objects.filter(
            competition=get_active_competition(self.request)
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["statuses_display"] = [
            TeamStatus(x).label for x in self.object.team_statuses
        ]
        ctx["venues_display"] = [
            str(x) for x in self.object.team_venues.select_related("category").all()
        ]
        ctx["team_count"] = self.object.get_teams().count()
        ctx["excluded_count"] = self.object.excluded_teams.count()
        ctx["can_edit"] = can_edit_campaign(self.request, self.object)
        return ctx


class CampaignTeamListView(AdminRequiredMixin, TemplateView):
    template_name = "bullet_admin/emails/teams.html"

    def dispatch(self, request, *args, **kwargs):
        if not self.can_access():
            return self.handle_fail()

        self.campaign = get_object_or_404(
            EmailCampaign,
            competition=get_active_competition(self.request),
            pk=kwargs["pk"],
        )
        if not can_edit_campaign(self.request, self.campaign):
            return self.handle_fail()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["teams"] = (
            self.campaign.get_teams(ignore_excluded=True)
            .select_related("school", "venue", "venue__category")
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


class CampaignSendTestView(AdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        campaign = get_object_or_404(
            EmailCampaign,
            competition=get_active_competition(self.request),
            pk=kwargs["pk"],
        )
        if not can_edit_campaign(self.request, campaign):
            raise PermissionDenied()
        team = campaign.get_teams().first()
        campaign.send_single(team, request.user.email)

        messages.success(request, "Testing email sent.")
        return HttpResponseRedirect(
            reverse("badmin:email_detail", kwargs={"pk": campaign.id})
        )


class CampaignSendView(AdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        campaign = get_object_or_404(
            EmailCampaign,
            competition=get_active_competition(self.request),
            pk=kwargs["pk"],
        )
        if not can_edit_campaign(self.request, campaign):
            raise PermissionDenied()

        campaign.send_all()
        campaign.last_sent = timezone.now()
        campaign.save()

        messages.success(request, "The campaign was sent successfully.")
        return HttpResponseRedirect(
            reverse("badmin:email_detail", kwargs={"pk": campaign.id})
        )
