from django.urls import path

from bullet_admin.views.files import (
    FileDeleteView,
    FileTreeView,
    FileUploadView,
    FolderCreateView,
)

urlpatterns = [
    path("", FileTreeView.as_view(), name="file_tree"),
    path("create_folder/", FolderCreateView.as_view(), name="file_create_folder"),
    path("upload/", FileUploadView.as_view(), name="file_upload"),
    path("delete/", FileDeleteView.as_view(), name="file_delete"),
]
