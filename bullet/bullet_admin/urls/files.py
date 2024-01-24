from django.urls import path

from bullet_admin.views.files import FileTreeView

urlpatterns = [
    path("", FileTreeView.as_view(), name="file_tree"),
]
