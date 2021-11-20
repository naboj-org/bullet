from django.contrib import admin
from web.models import Translation


@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    pass
