from django.contrib import admin
from web.models import ContentBlock, Menu, Organizer, Page, Partner, Translation


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ["title", "branch", "language", "countries", "slug"]
    list_filter = ["branch", "language", "slug"]


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
    list_display = ["title", "branch", "language", "countries", "slug", "order"]
    list_filter = ["branch", "language", "slug"]


@admin.register(ContentBlock)
class ContentBlockAdmin(admin.ModelAdmin):
    list_filter = ["branch", "country", "language"]
    list_display = ["reference", "branch", "country", "language"]
