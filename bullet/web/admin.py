from django.contrib import admin
from web.models import Menu, Organizer, Page, Partner, Translation


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ["title", "branch", "language", "url"]
    list_filter = ["branch", "language"]


@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    pass


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    pass


@admin.register(Organizer)
class OrganizerAdmin(admin.ModelAdmin):
    pass


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ["title", "branch", "url"]
    list_filter = ["branch", "url"]
