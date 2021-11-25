from django.contrib import admin
from web.models import Page, Translation


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ["title", "branch", "language", "url"]
    list_filter = ["branch", "language"]


@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    pass
