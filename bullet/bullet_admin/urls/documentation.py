from django.urls import path

from bullet_admin.views.documentation import DocumentationHomeView, DocumentationView

urlpatterns = [
    path("", DocumentationHomeView.as_view(), name="documentation"),
    path("<slug>/", DocumentationView.as_view(), name="documentation"),
]
