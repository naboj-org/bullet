from django.urls import path

from bullet_admin.views.wildcards import (
    WildcardCreateView,
    WildcardDeleteView,
    WildcardListView,
)

urlpatterns = [
    path("", WildcardListView.as_view(), name="wildcard_list"),
    path("create/", WildcardCreateView.as_view(), name="wildcard_create"),
    path("<int:pk>/delete/", WildcardDeleteView.as_view(), name="wildcard_delete"),
]
