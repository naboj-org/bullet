from bullet_admin.views import (
    CompetitionSwitchView,
    auth,
    content,
    documents,
    emails,
    home,
    results,
    scanning,
    teams,
    users,
    venues,
)
from django.urls import path

app_name = "badmin"
urlpatterns = [
    path("", home.HomeView.as_view(), name="home"),
    path("auth/login/", auth.LoginView.as_view(), name="login"),
    path("auth/logout/", auth.LogoutView.as_view(), name="logout"),
    path(
        "auth/password_change/",
        auth.PasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "auth/password_reset/",
        auth.PasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "auth/password_reset/<uidb64>/<token>/",
        auth.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
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
    path(
        "content/logos/",
        content.LogoListView.as_view(),
        name="logo_list",
    ),
    path(
        "content/logos/edit/<pk>/",
        content.LogoEditView.as_view(),
        name="logo_edit",
    ),
    path(
        "content/logos/create/",
        content.LogoCreateView.as_view(),
        name="logo_create",
    ),
    path(
        "content/logos/delete/<pk>/",
        content.LogoDeleteView.as_view(),
        name="logo_delete",
    ),
    path(
        "content/menu/",
        content.MenuItemListView.as_view(),
        name="menu_list",
    ),
    path(
        "content/menu/edit/<pk>/",
        content.MenuItemEditView.as_view(),
        name="menu_edit",
    ),
    path(
        "content/menu/delete/<pk>/",
        content.MenuItemDeleteView.as_view(),
        name="menu_delete",
    ),
    path(
        "content/menu/create/",
        content.MenuItemCreateView.as_view(),
        name="menu_create",
    ),
    path("teams/", teams.TeamListView.as_view(), name="team_list"),
    path(
        "teams/assign_numbers/",
        teams.AssignTeamNumbersView.as_view(),
        name="team_assign_numbers",
    ),
    path("teams/<int:pk>/", teams.TeamEditView.as_view(), name="team_edit"),
    path(
        "teams/<int:pk>/to_competition/",
        teams.TeamToCompetitionView.as_view(),
        name="team_to_competition",
    ),
    path(
        "teams/<int:pk>/resend_confirmation/",
        teams.TeamResendConfirmationView.as_view(),
        name="team_resend_confirmation",
    ),
    path(
        "teams/<int:pk>/delete/",
        teams.TeamDeleteView.as_view(),
        name="team_delete",
    ),
    path("teams/waiting/", teams.WaitingListView.as_view(), name="waiting_list"),
    path(
        "teams/waiting/automove/",
        teams.WaitingAutomoveView.as_view(),
        name="waiting_automove",
    ),
    path("_school_input", teams.SchoolInputView.as_view(), name="school_input"),
    path("users/", users.UserListView.as_view(), name="user_list"),
    path("users/create/", users.UserCreateView.as_view(), name="user_create"),
    path("users/<int:pk>/", users.UserEditView.as_view(), name="user_edit"),
    path(
        "scanning/problems/",
        scanning.ProblemScanView.as_view(),
        name="scanning_problems",
    ),
    path(
        "scanning/review/",
        scanning.VenueReviewView.as_view(),
        name="scanning_review",
    ),
    path("scanning/problems/api/", scanning.ApiProblemSolveView.as_view()),
    path("emails/", emails.CampaignListView.as_view(), name="email_list"),
    path("emails/create/", emails.CampaignCreateView.as_view(), name="email_create"),
    path(
        "emails/<int:pk>/edit/", emails.CampaignUpdateView.as_view(), name="email_edit"
    ),
    path("emails/<int:pk>/", emails.CampaignDetailView.as_view(), name="email_detail"),
    path(
        "emails/<int:pk>/teams/",
        emails.CampaignTeamListView.as_view(),
        name="email_teams",
    ),
    path(
        "emails/<int:pk>/test/",
        emails.CampaignSendTestView.as_view(),
        name="email_test",
    ),
    path(
        "emails/<int:pk>/send/",
        emails.CampaignSendView.as_view(),
        name="email_send",
    ),
    path(
        "documents/certificates/",
        documents.CertificateView.as_view(),
        name="docs_certificates",
    ),
    path(
        "documents/team_lists/",
        documents.TeamListView.as_view(),
        name="docs_teamlists",
    ),
    path("results/", results.ResultsHomeView.as_view(), name="results"),
    path(
        "results/announce/<venue>/",
        results.ResultsAnnouncementView.as_view(),
        name="results_announce",
    ),
    path("venues/", venues.VenueListView.as_view(), name="venue_list"),
    path("venues/<int:pk>/", venues.VenueUpdateView.as_view(), name="venue_update"),
    path("venues/create/", venues.VenueCreateView.as_view(), name="venue_create"),
]
