from countries.models import BranchCountry
from django.contrib import admin


@admin.register(BranchCountry)
class BranchCountryAdmin(admin.ModelAdmin):
    list_display = ["branch", "country", "languages"]
    list_filter = ["branch"]
