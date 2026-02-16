from django.urls.conf import path

from bullet_admin.views import album

urlpatterns = [
    path(
        "",
        album.AlbumListView.as_view(),
        name="album_list",
    ),
    path(
        "create/",
        album.AlbumCreateView.as_view(),
        name="album_create",
    ),
    path(
        "<int:pk>/",
        album.AlbumUpdateView.as_view(),
        name="album_update",
    ),
    path(
        "<int:pk>/photos/",
        album.AlbumPhotoListView.as_view(),
        name="album_photo_list",
    ),
    path(
        "<int:pk>/photos/upload/",
        album.AlbumUploadView.as_view(),
        name="album_upload",
    ),
    path(
        "<int:album_pk>/photos/<int:pk>/",
        album.AlbumPhotoDeleteView.as_view(),
        name="album_photo_delete",
    ),
    path(
        "<int:pk>/delete/",
        album.AlbumDeleteView.as_view(),
        name="album_delete",
    ),
]
