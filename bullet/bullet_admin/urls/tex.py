from django.urls import path

from bullet_admin.views.tex import (
    JobDetailView,
    LetterCallbackView,
    TemplateCreateView,
    TemplateListView,
    TemplateRenderView,
    TemplateUpdateView,
)

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
    path(
        "templates/",
        TemplateListView.as_view(),
        name="tex_template_list",
    ),
    path(
        "templates/create/",
        TemplateCreateView.as_view(),
        name="tex_template_create",
    ),
    path(
        "templates/<int:pk>/",
        TemplateUpdateView.as_view(),
        name="tex_template_update",
    ),
    path(
        "templates/<int:pk>/render/",
        TemplateRenderView.as_view(),
        name="tex_template_render",
    ),
]
