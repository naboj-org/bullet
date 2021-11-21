from django.contrib import admin
from web.models import Page, Translation


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    pass


@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    pass
