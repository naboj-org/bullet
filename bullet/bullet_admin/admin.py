from bullet_admin.models import BranchRole, CompetitionRole
from competitions.models import Venue
from django.contrib import admin


@admin.register(BranchRole)
class BranchRoleAdmin(admin.ModelAdmin):
    list_display = ("branch", "user", "is_translator", "is_admin")
    list_filter = ("branch",)
    autocomplete_fields = ("user",)


@admin.register(CompetitionRole)
class CompetitionRoleAdmin(admin.ModelAdmin):
    list_display = ("competition", "user", "country_list", "venue_list")
    list_filter = ("competition",)
    autocomplete_fields = ("user",)

    def venue_list(self, obj):
        return ", ".join([v.name for v in obj.venues])

    def country_list(self, obj):
        return ", ".join(obj.countries) if obj.countries else ""

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "venue_objects":
            kwargs["queryset"] = Venue.objects.select_related("category_competition")
        return super().formfield_for_manytomany(db_field, request, **kwargs)
