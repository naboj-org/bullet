from django.contrib import admin

from web.models import ContentBlock, Logo, Menu, Page, PageBlock

admin.site.site_title = "Bullet system administration"
admin.site.site_header = "Bullet system administration"


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ["title", "branch", "language", "countries", "slug"]
    list_filter = ["branch", "language", "slug"]


@admin.register(Logo)
class LogoAdmin(admin.ModelAdmin):
    list_display = ["branch", "type", "name", "countries"]
    list_filter = ["branch", "type"]


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ["title", "branch", "language", "countries", "url", "order"]
    list_filter = ["branch", "language", "url"]


@admin.register(ContentBlock)
class ContentBlockAdmin(admin.ModelAdmin):
    list_filter = ["branch", "country", "language"]
    list_display = ["reference", "branch", "country", "language"]


@admin.register(PageBlock)
class PageBlockAdmin(admin.ModelAdmin):
    list_display = ["page", "order", "block_type", "states"]
