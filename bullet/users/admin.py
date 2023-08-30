from competitions.models import Venue
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from education.models import Grade
from simple_history.admin import SimpleHistoryAdmin
from users.models import Contestant, Team, User


@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    list_display = ("email", "first_name", "last_name", "is_staff")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("first_name", "last_name", "email")
    ordering = ("email",)


class TeamContestantInlineAdmin(admin.TabularInline):
    model = Contestant
    extra = 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "grade":
            kwargs["queryset"] = Grade.objects.select_related("school_type")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Team)
class TeamAdmin(SimpleHistoryAdmin):
    inlines = (TeamContestantInlineAdmin,)
    list_display = (
        "school",
        "venue",
        "contact_email",
        "language",
        "is_reviewed",
    )
    search_fields = (
        "school__name",
        "school__address",
        "venue__name",
    )
    list_select_related = (
        "school",
        "venue",
        "venue__category",
        "venue__category__competition",
    )
    autocomplete_fields = (
        "venue",
        "school",
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "venue":
            kwargs["queryset"] = Venue.objects.select_related(
                "category",
                "category__competition",
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Contestant)
class ContestantAdmin(SimpleHistoryAdmin):
    autocomplete_fields = ("team",)
    list_select_related = ("grade__school_type",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "grade":
            kwargs["queryset"] = Grade.objects.select_related("school_type")
        if db_field.name == "team":
            kwargs["queryset"] = Team.objects.select_related(
                "school",
                "venue",
                "venue__category",
                "venue__category__competition",
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
