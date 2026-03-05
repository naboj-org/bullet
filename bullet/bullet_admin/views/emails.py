from functools import cached_property

from competitions.models.venues import Venue
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
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

from bullet_admin.access import PermissionCheckMixin, is_admin, is_branch_admin
from bullet_admin.forms.emails import EmailCampaignForm
from bullet_admin.utils import get_active_competition
from bullet_admin.views.generic.links import Link, NewLink, ViewIcon
from bullet_admin.views.generic.list import GenericList


def can_edit_campaign(request, campaign: EmailCampaign):
    user: User = request.user
    competition = get_active_competition(request)

    # Branch admins can edit all campaigns
    if is_branch_admin(user, competition):
        return True

    # Only branch admin can edit global emails (no country/venue filters)
    if not campaign.team_countries and not campaign.team_venues.exists():
        return False

    crole = user.get_competition_role(competition)

    # Country admin can edit campaigns targeting ANY of their countries
    if crole.countries:
        user_countries = set(crole.countries)
        campaign_countries = set(campaign.team_countries)

        # Campaign must target at least one of the user's countries
        if campaign_countries and not user_countries.issuperset(campaign_countries):
            return False

        # Any venues in the campaign must be in the user's countries
        campaign_venue_countries = set(
            campaign.team_venues.values_list("country", flat=True)
        )
        if campaign_venue_countries and not user_countries.issuperset(
            campaign_venue_countries
        ):
            return False

    # Venue admin can edit campaigns targeting ANY of their venues
    venues = crole.venues
    if venues:
        # Venue admins cannot edit country-targeted campaigns
        if campaign.team_countries:
            return False

        user_venues = set(venues)
        campaign_venues = set(campaign.team_venues.all())

        # Campaign must target at least one of the user's venues
        if campaign_venues and not user_venues.issuperset(campaign_venues):
            return False

    return True


class CampaignListView(PermissionCheckMixin, GenericList, ListView):
    required_permissions = [is_admin]
    list_links = [NewLink("campaign", reverse_lazy("badmin:email_create"))]
    table_fields = ["subject", "last_sent"]
    filter_country_permissions = False

    def get_queryset(self):
        assert isinstance(self.request.user, User)
        competition = get_active_competition(self.request)
        qs = EmailCampaign.objects.filter(competition=competition)

        # Branch admins see all campaigns
        if is_branch_admin(self.request.user, competition):
            return qs

        crole = self.request.user.get_competition_role(competition)

        # Country admins see campaigns targeting their countries or venues in their countries
        if crole.countries:
            # Campaigns with countries in the user's scope
            campaigns_with_matching_countries = Q(
                team_countries__contained_by=crole.countries
            ) & ~Q(team_countries=[])

            # Campaigns with venues in the user's countries
            venues_in_other_countries = Venue.objects.filter(
                category__competition=competition
            ).exclude(country__in=crole.countries)
            campaigns_with_venues_in_user_countries = Q(
                team_venues__country__in=crole.countries
            )

            qs = qs.filter(
                campaigns_with_matching_countries
                | campaigns_with_venues_in_user_countries
            ).exclude(team_venues__in=venues_in_other_countries)

        # Venue admins (without country admin) see campaigns targeting their venues only
        elif crole.venues:
            all_other_venues = Venue.objects.filter(
                category__competition=competition
            ).exclude(id__in=crole.venues)

            qs = qs.filter(team_venues__in=crole.venues, team_countries=[]).exclude(
                team_venues__in=all_other_venues
            )

        return qs.distinct()

    def get_row_links(self, obj) -> list[Link]:
        return [ViewIcon(reverse("badmin:email_detail", args=[obj.pk]))]


class CampaignCreateView(PermissionCheckMixin, CreateView):
    required_permissions = [is_admin]
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


class CampaignUpdateView(PermissionCheckMixin, UpdateView):
    required_permissions = [is_admin]
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


class CampaignDetailView(PermissionCheckMixin, DetailView):
    required_permissions = [is_admin]
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


class CampaignTeamListView(PermissionCheckMixin, TemplateView):
    required_permissions = [is_admin]
    template_name = "bullet_admin/emails/teams.html"

    @cached_property
    def campaign(self):
        return get_object_or_404(
            EmailCampaign,
            competition=get_active_competition(self.request),
            pk=self.kwargs["pk"],
        )

    def check_custom_permission(self, user: User) -> bool | None:
        """
        Branch admins can edit all campaigns.
        Country admins can edit campaigns targeting at least one of their countries.
        Venue admins can edit campaigns targeting at least one of their venues (but not country-targeted campaigns).
        """
        return can_edit_campaign(self.request, self.campaign)

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


class CampaignSendTestView(PermissionCheckMixin, View):
    required_permissions = [is_admin]

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


class CampaignSendView(PermissionCheckMixin, View):
    required_permissions = [is_admin]

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
