from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from users.models import Contestant, Team, User


@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    pass


class TeamParticipantAdmin(admin.TabularInline):
    model = Contestant
    extra = 0


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    inlines = (TeamParticipantAdmin,)
    list_display = (
        "school",
        "competition_venue",
        "contact_email",
        "language",
        "is_reviewed",
    )


@admin.register(Contestant)
class ParticipantAdmin(admin.ModelAdmin):
    pass
