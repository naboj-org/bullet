from django.urls import path

from bullet_admin.views.tex import JobDetailView, LetterCallbackView

urlpatterns = [
    path(
        "jobs/<uuid:pk>/callback/",
        LetterCallbackView.as_view(),
        name="tex_letter_callback",
    ),
    path(
        "jobs/<uuid:pk>/",
        JobDetailView.as_view(),
        name="tex_job_detail",
    ),
]
