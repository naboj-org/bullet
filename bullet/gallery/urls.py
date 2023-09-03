from django.urls import path
from gallery.views import album

urlpatterns = [
    path(
        "archive/<int:competition_number>/albums/<slug>/",
        album.AlbumView.as_view(),
        name="archive_album",
    ),
    path(
        "archive/<int:competition_number>/albums/",
        album.AlbumListView.as_view(),
        name="archive_album_list",
    ),
]
