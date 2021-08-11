from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

from users.models import User, Team, Participant, School


@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    pass


class TeamParticipantAdmin(admin.TabularInline):
    model = Participant
    extra = 0


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    inlines = (TeamParticipantAdmin, )
    list_display = ('school', 'competition_site', 'contact_email', 'language', 'is_reviewed')


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    pass


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'address', 'izo')
