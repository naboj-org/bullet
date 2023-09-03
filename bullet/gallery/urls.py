from django.urls import path
from gallery.views import album

urlpatterns = [
    path(
        "archive/<int:competition_number>/country/<country>/album/<slug>/",
        album.AlbumView.as_view(),
        name="archive_album",
    ),
]
