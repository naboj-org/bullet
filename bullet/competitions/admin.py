from competitions.models import (
    CategoryCompetition,
    Competition,
    CompetitionVenue,
    Venue,
    Wildcard,
)
from django.contrib import admin


class CategoryCompetitionInlineAdmin(admin.TabularInline):
    extra = 0
    model = CategoryCompetition


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    inlines = (CategoryCompetitionInlineAdmin,)
    list_display = (
        "name",
        "branch",
        "registration_start",
        "registration_end",
        "competition_start",
    )


class CompetitionVenueInlineAdmin(admin.TabularInline):
    model = CompetitionVenue
    extra = 0


@admin.register(CategoryCompetition)
class CategoryCompetitionAdmin(admin.ModelAdmin):
    inlines = (CompetitionVenueInlineAdmin,)
    list_display = (
        "competition",
        "identifier",
        "problems_per_team",
        "max_teams_per_school",
        "max_members_per_team",
        "ranking",
    )


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "short_name", "address")


@admin.register(CompetitionVenue)
class CompetitionVenueAdmin(admin.ModelAdmin):
    list_display = (
        "venue",
        "category_competition",
        "capacity",
        "accepted_languages",
        "local_start",
    )


@admin.register(Wildcard)
class WildcardAdmin(admin.ModelAdmin):
    pass
