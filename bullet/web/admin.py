from django.contrib import admin
from web.models import Menu, Page, Translation


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ["title", "branch", "language", "url"]
    list_filter = ["branch", "language"]


@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    pass


@admin.register(Menu)
class PageAdmin(admin.ModelAdmin):
    list_display = ["title", "branch", "url"]
    list_filter = ["branch", "url"]
