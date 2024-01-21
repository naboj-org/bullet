from django.contrib import admin

from competitions.models import Category, Competition, Venue, Wildcard


class CategoryInlineAdmin(admin.TabularInline):
    extra = 0
    model = Category


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    inlines = (CategoryInlineAdmin,)
    list_display = (
        "name",
        "branch",
        "registration_start",
        "registration_end",
        "competition_start",
    )


class CompetitionVenueInlineAdmin(admin.TabularInline):
    model = Venue
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = (CompetitionVenueInlineAdmin,)
    list_display = (
        "competition",
        "identifier",
        "problems_per_team",
        "max_teams_per_school",
        "max_members_per_team",
    )


@admin.register(Venue)
class CompetitionVenueAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "capacity",
        "accepted_languages",
        "local_start",
    )
    search_fields = (
        "name",
        "shortcode",
    )


@admin.register(Wildcard)
class WildcardAdmin(admin.ModelAdmin):
    pass
