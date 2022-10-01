from bullet_admin.views import CompetitionSwitchView, auth, content, home, teams
from django.urls import path

app_name = "badmin"
urlpatterns = [
    path("", home.HomeView.as_view(), name="home"),
    path("login/", auth.LoginView.as_view(), name="login"),
    path("competitions/", CompetitionSwitchView.as_view(), name="competition_switch"),
    path("content/pages/", content.PageListView.as_view(), name="page_list"),
    path("content/pages/new/", content.PageCreateView.as_view(), name="page_create"),
    path("content/pages/<pk>/", content.PageEditView.as_view(), name="page_edit"),
    path(
        "content/pages/<pk>/delete/",
        content.PageDeleteView.as_view(),
        name="page_delete",
    ),
    path(
        "content/blocks/",
        content.ContentBlockListView.as_view(),
        name="contentblock_list",
    ),
    path(
        "content/blocks/trans/<group>/<reference>/",
        content.ContentBlockTranslationListView.as_view(),
        name="contentblock_trans",
    ),
    path(
        "content/blocks/new/",
        content.ContentBlockCreateView.as_view(),
        name="contentblock_create",
    ),
    path(
        "content/blocks/edit/<pk>/",
        content.ContentBlockEditView.as_view(),
        name="contentblock_edit",
    ),
    path(
        "content/blocks/delete/<pk>/",
        content.ContentBlockDeleteView.as_view(),
        name="contentblock_delete",
    ),
    path("teams/", teams.TeamListView.as_view(), name="team_list"),
    path("teams/waiting/", teams.WaitingListView.as_view(), name="waiting_list"),
]
