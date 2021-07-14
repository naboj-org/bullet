from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

from users.models import User, Team, Participant, School


@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    pass


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    pass


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    pass


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    pass
