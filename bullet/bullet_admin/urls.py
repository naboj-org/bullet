from bullet_admin.views import auth, home
from django.urls import path

app_name = "badmin"
urlpatterns = [
    path("", home.HomeView.as_view(), name="home"),
    path("login/", auth.LoginView.as_view(), name="login"),
]
