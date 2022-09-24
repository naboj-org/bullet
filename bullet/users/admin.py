from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
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


class TeamContestantAdmin(admin.TabularInline):
    model = Contestant
    extra = 0


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    inlines = (TeamContestantAdmin,)
    list_display = (
        "school",
        "competition_venue",
        "contact_email",
        "language",
        "is_reviewed",
    )


@admin.register(Contestant)
class ContestantAdmin(admin.ModelAdmin):
    pass
