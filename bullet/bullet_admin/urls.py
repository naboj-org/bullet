from bullet_admin.views import auth, content, home
from django.urls import path

app_name = "badmin"
urlpatterns = [
    path("", home.HomeView.as_view(), name="home"),
    path("login/", auth.LoginView.as_view(), name="login"),
    path("content/pages/", content.PageListView.as_view(), name="page_list"),
    path("content/pages/new/", content.PageCreateView.as_view(), name="page_create"),
    path("content/pages/<pk>/", content.PageEditView.as_view(), name="page_edit"),
    path(
        "content/pages/<pk>/delete/",
        content.PageDeleteView.as_view(),
        name="page_delete",
    ),
]
