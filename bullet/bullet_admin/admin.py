from django.contrib import admin

from bullet_admin.models import BranchRole, CompetitionRole


@admin.register(BranchRole)
class BranchRoleAdmin(admin.ModelAdmin):
    list_display = ("branch", "user", "is_admin")
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
