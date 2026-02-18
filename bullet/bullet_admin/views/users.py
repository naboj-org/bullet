import secrets
from functools import partial

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Exists, F, OuterRef, Prefetch, Q, Value
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.utils.safestring import mark_safe
from django.views import View
from django.views.generic import ListView
from django_countries.fields import Country
from users.emails.users import send_onboarding_email
from users.models import User

from bullet_admin.access import PermissionCheckMixin, is_admin
from bullet_admin.forms.users import BranchRoleForm, CompetitionRoleForm, UserForm
from bullet_admin.models import BranchRole, CompetitionRole
from bullet_admin.utils import get_active_competition
from bullet_admin.views.generic.links import EditIcon, Link, NewLink
from bullet_admin.views.generic.list import GenericList, MixinProtocol

PASSWORD_ALPHABET = "346789ABCDEFGHJKLMNPQRTUVWXY"


class PermissionFiltering(MixinProtocol):
    """Mixin for filtering by user permissions (branch admin, country admin, venue admin)."""

    def apply_permission_filter(self, qs):
        """Apply permission filters to the queryset."""
        branch_admin = self.request.GET.get("branch_admin")
        country_admin = self.request.GET.get("country_admin")
        venue_admin = self.request.GET.get("venue_admin")

        # If no permission filters are set, return queryset as-is
        if not (branch_admin or country_admin or venue_admin):
            return qs

        # Build filters for users with specific permissions
        filters = Q()

        if branch_admin:
            branch_role_exists = BranchRole.objects.filter(
                branch=self.request.BRANCH, user=OuterRef("pk"), is_admin=True
            )
            filters |= Q(Exists(branch_role_exists))

        if country_admin or venue_admin:
            competition = get_active_competition(self.request)
            competition_role_exists = CompetitionRole.objects.filter(
                competition=competition, user=OuterRef("pk")
            )

            if country_admin:
                competition_role_exists = competition_role_exists.filter(
                    countries__len__gt=0
                )
            if venue_admin:
                competition_role_exists = competition_role_exists.filter(
                    venue_objects__isnull=False
                )

            filters |= Q(Exists(competition_role_exists))

        return qs.filter(filters)

    def get_permission_filters(self) -> dict[str, bool]:
        """Return the active permission filters as a dictionary."""
        return {
            "branch_admin": self.request.GET.get("branch_admin") == "on",
            "country_admin": self.request.GET.get("country_admin") == "on",
            "venue_admin": self.request.GET.get("venue_admin") == "on",
        }


class UserListView(PermissionCheckMixin, PermissionFiltering, GenericList, ListView):
    required_permissions = [is_admin]
    list_links = [NewLink("user", reverse_lazy("badmin:user_create"))]
    template_name = "bullet_admin/users/list.html"

    table_fields = ["get_full_name", "email", "competition_permissions"]
    table_labels = {
        "get_full_name": "Full Name",
        "competition_permissions": "Permissions",
    }
    unsortable_fields = ["competition_permissions"]

    def get_queryset(self):
        qs = (
            User.objects.order_by("email")
            .annotate(
                get_full_name=Concat(F("first_name"), Value(" "), F("last_name")),
            )
            .prefetch_related(
                Prefetch(
                    "branchrole_set",
                    queryset=BranchRole.objects.filter(branch=self.request.BRANCH),
                    to_attr="branch_role_for_list",
                ),
                Prefetch(
                    "competitionrole_set",
                    queryset=CompetitionRole.objects.filter(
                        competition=get_active_competition(self.request)
                    ).prefetch_related("venue_objects"),
                    to_attr="competition_role_for_list",
                ),
            )
        )

        return self.apply_permission_filter(qs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["permission_filters"] = self.get_permission_filters()
        return ctx

    def get_competition_permissions_content(self, obj):
        permissions = []

        # Get branch role from prefetched data
        branch_roles = getattr(obj, "branch_role_for_list", [])
        if branch_roles and branch_roles[0].is_admin:
            permissions.append("Branch admin")

        # Get competition role from prefetched data
        competition_roles = getattr(obj, "competition_role_for_list", [])
        if competition_roles:
            crole = competition_roles[0]

            if crole.countries:
                countries = [str(c) for c in crole.countries]
                if len(countries) <= 2:
                    permissions.append(f"Country admin: {', '.join(countries)}")
                else:
                    permissions.append(
                        f"Country admin: {', '.join(countries[:2])} +{len(countries) - 2}"
                    )

            if crole.venues:
                venues = [str(v) for v in crole.venues]
                if len(venues) <= 2:
                    permissions.append(f"Venue admin: {', '.join(venues)}")
                else:
                    permissions.append(
                        f"Venue admin: {', '.join(venues[:2])} +{len(venues) - 2}"
                    )

        return (
            mark_safe("<br>".join(permissions))
            if permissions
            else mark_safe('<span class="text-gray-400">-</span>')
        )

    def get_row_links(self, obj) -> list[Link]:
        return [EditIcon(reverse("badmin:user_edit", args=[obj.pk]))]


class UserFormsMixin:
    def get_forms(self, request, user=None):
        data = None
        if request.method == "POST":
            data = request.POST
        form = UserForm(data=data, instance=user)
        bform = None
        cform = None

        brole = self.request.user.get_branch_role(self.request.BRANCH)
        if brole.is_admin:
            instance = None
            if user:
                instance = user.get_branch_role(self.request.BRANCH)
            bform = BranchRoleForm(
                data=data,
                instance=instance,
            )

        competition = get_active_competition(self.request)
        crole = self.request.user.get_competition_role(competition)
        if brole.is_admin or crole.countries or crole.venues:
            instance = None
            if user:
                instance = user.get_competition_role(competition)

            allowed_objects = None
            if crole.countries:
                allowed_objects = [Country(code) for code in crole.countries]
            elif crole.venues:
                allowed_objects = crole.venues

            cform = CompetitionRoleForm(
                data=data,
                instance=instance,
                competition=competition,
                allowed_objects=allowed_objects,
            )

        return form, bform, cform


class UserCreateView(PermissionCheckMixin, UserFormsMixin, View):
    required_permissions = [is_admin]

    def get(self, request, *args, **kwargs):
        form, bform, cform = self.get_forms(request)

        return TemplateResponse(
            request,
            "bullet_admin/users/form.html",
            {"form": form, "bform": bform, "cform": cform},
        )

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form, bform, cform = self.get_forms(request)

        if (
            not form.is_valid()
            or (bform and not bform.is_valid())
            or (cform and not cform.is_valid())
        ):
            return TemplateResponse(
                request,
                "bullet_admin/users/form.html",
                {"form": form, "bform": bform, "cform": cform},
            )

        user: User = form.save(commit=False)
        passwd = "".join(secrets.choice(PASSWORD_ALPHABET) for i in range(8))
        user.set_password(passwd)
        user.save()

        brole = None
        if bform:
            brole = bform.save(commit=False)
            brole.user = user
            brole.branch = request.BRANCH
            brole.save()

        if cform and (not brole or not brole.is_admin):
            crole = cform.save(commit=False)
            crole.user = user
            crole.competition = get_active_competition(request)
            crole.save()
            cform.save_m2m()

        transaction.on_commit(
            partial(send_onboarding_email.delay, request.BRANCH, user.id, passwd)
        )
        messages.success(request, "The user was created.")
        return HttpResponseRedirect(reverse("badmin:user_list"))


class UserEditView(PermissionCheckMixin, UserFormsMixin, View):
    required_permissions = [is_admin]

    def can_edit_user(self, target: User):
        user: User = self.request.user
        competition = get_active_competition(self.request)
        branch = self.request.BRANCH

        # Branch admin can edit any user
        if user.get_branch_role(branch).is_admin:
            return True

        # Branch admin can only be edited by another branch admin
        if target.get_branch_role(branch).is_admin:
            return False

        target_crole = target.get_competition_role(competition)
        user_crole = user.get_competition_role(competition)

        # Country admin can only be edited by country admin from the same country
        if target_crole.countries:
            return set(target_crole.countries).issubset(set(user_crole.countries))

        # Venue admin can only be edited by admin from the same
        # venue or admin from venues' country
        if target_crole.venues:
            if user_crole.venues:
                return set(target_crole.venues).issubset(set(user_crole.venues))

            return all(
                venue.country in user_crole.countries for venue in target_crole.venues
            )

        return True

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs["pk"])
        if not self.can_edit_user(user):
            messages.error(
                request,
                "You can't edit this user because he/she has more privileges than you.",
            )
            return HttpResponseRedirect(reverse("badmin:user_list"))

        form, bform, cform = self.get_forms(request, user)

        return TemplateResponse(
            request,
            "bullet_admin/users/form.html",
            {"form": form, "bform": bform, "cform": cform, "object": user},
        )

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs["pk"])
        if not self.can_edit_user(user):
            raise PermissionDenied()

        form, bform, cform = self.get_forms(request, user)

        if (
            not form.is_valid()
            or (bform and not bform.is_valid())
            or (cform and not cform.is_valid())
        ):
            return TemplateResponse(
                request,
                "bullet_admin/users/form.html",
                {"form": form, "bform": bform, "cform": cform, "object": user},
            )

        user = form.save()

        brole = None
        if bform:
            brole = bform.save(commit=False)
            brole.user = user
            brole.branch = request.BRANCH
            brole.save()

        if cform and (not brole or not brole.is_admin):
            crole = cform.save(commit=False)
            crole.user = user
            crole.competition = get_active_competition(request)
            crole.save()
            cform.save_m2m()

        messages.success(request, "The user was edited.")
        return HttpResponseRedirect(reverse("badmin:user_list"))
