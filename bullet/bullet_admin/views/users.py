from functools import partial

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Exists, OuterRef, Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView
from django_countries.fields import Country
from users.emails.users import send_onboarding_email
from users.models import User

from bullet_admin.forms.users import BranchRoleForm, CompetitionRoleForm, UserForm
from bullet_admin.mixins import DelegateRequiredMixin
from bullet_admin.models import BranchRole, CompetitionRole
from bullet_admin.utils import get_active_competition
from bullet_admin.views import GenericList
import secrets


PASSWORD_ALPHABET = "346789ABCDEFGHJKLMNPQRTUVWXY"


class UserListView(DelegateRequiredMixin, GenericList, ListView):
    create_url = reverse_lazy("badmin:user_create")
    fields = ["get_full_name", "email", "has_branch_role"]
    labels = {"get_full_name": "Full Name", "has_branch_role": "Admin access"}
    field_templates = {"has_branch_role": "bullet_admin/users/role.html"}

    def get_queryset(self):
        branch_role = BranchRole.objects.filter(
            branch=self.request.BRANCH, user=OuterRef("pk")
        ).filter(Q(is_admin=True) | Q(is_translator=True))
        competition_role = CompetitionRole.objects.filter(
            competition=get_active_competition(self.request), user=OuterRef("pk")
        ).filter(Q(venue_objects__isnull=False) | Q(countries__len__gt=0))

        qs = User.objects.order_by("email").annotate(
            has_branch_role=Exists(branch_role),
            has_competition_role=Exists(competition_role),
        )

        return qs

    def get_edit_url(self, user: User) -> str:
        return reverse("badmin:user_edit", args=[user.pk])


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


class UserCreateView(DelegateRequiredMixin, UserFormsMixin, View):
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
        passwd = ''.join(secrets.choice(PASSWORD_ALPHABET) for i in range(8))
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


class UserEditView(DelegateRequiredMixin, UserFormsMixin, View):
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
