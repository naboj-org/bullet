from countries.models import BranchCountry
from django.contrib import admin


@admin.register(BranchCountry)
class BranchCountryAdmin(admin.ModelAdmin):
    pass
