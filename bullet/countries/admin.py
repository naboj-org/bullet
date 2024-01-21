from django.contrib import admin

from countries.models import BranchCountry


@admin.register(BranchCountry)
class BranchCountryAdmin(admin.ModelAdmin):
    list_display = ["branch", "country", "languages", "timezone"]
    list_filter = ["branch"]
