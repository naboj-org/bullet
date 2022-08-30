from django.shortcuts import render
from django.urls import path


def test(req):
    return render(req, "bullet_admin/base.html")


urlpatterns = [
    path("", test),
]
