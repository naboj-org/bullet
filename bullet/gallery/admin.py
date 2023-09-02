from django.contrib import admin
from gallery.models import Album, Photo


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ["title", "competition", "country"]
    list_filter = ["title", "competition", "country"]


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ["album"]
    list_filter = ["album"]
