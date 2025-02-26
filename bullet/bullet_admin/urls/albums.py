from django.urls.conf import path

from bullet_admin.views import albums

urlpatterns = [
    path(
        "",
        albums.AlbumListView.as_view(),
        name="album_list",
    ),
    path(
        "create/",
        albums.AlbumCreateView.as_view(),
        name="album_create",
    ),
    path(
        "<int:pk>/",
        albums.AlbumUpdateView.as_view(),
        name="album_update",
    ),
    path(
        "<int:pk>/photos/",
        albums.AlbumPhotoListView.as_view(),
        name="album_photo_list",
    ),
    path(
        "<int:pk>/photos/upload/",
        albums.AlbumUploadView.as_view(),
        name="album_upload",
    ),
    path(
        "<int:album_pk>/photos/<int:pk>/",
        albums.AlbumPhotoDeleteView.as_view(),
        name="album_photo_delete",
    ),
    path(
        "<int:pk>/delete/",
        albums.AlbumDeleteView.as_view(),
        name="album_delete",
    ),
]
