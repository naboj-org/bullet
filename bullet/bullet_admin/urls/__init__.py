from django.urls import include, path

from bullet_admin.views import (
    CompetitionSwitchView,
    album,
    archive,
    auth,
    category,
    competition,
    content,
    education,
    emails,
    home,
    results,
    scanning,
    teams,
    users,
)

app_name = "badmin"
urlpatterns = [
    path("", home.HomeView.as_view(), name="home"),
    path("release_notes/", home.ReleaseNotesView.as_view(), name="release_notes"),
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
    path(
        "competitions/edit/",
        competition.CompetitionUpdateView.as_view(),
        name="competition_edit",
    ),
    path(
        "competitions/new/",
        competition.CompetitionCreateView.as_view(),
        name="competition_create",
    ),
    path(
        "competitions/finalize/",
        competition.CompetitionFinalizeView.as_view(),
        name="competition_finalize",
    ),
    path(
        "competitions/tearoff_upload/",
        competition.CompetitionTearoffUploadView.as_view(),
        name="competition_upload_tearoffs",
    ),
    path(
        "competitions/automove/",
        competition.CompetitionAutomoveView.as_view(),
        name="competition_automove",
    ),
    path("categories/", category.CategoryListView.as_view(), name="category_list"),
    path(
        "categories/new", category.CategoryCreateView.as_view(), name="category_create"
    ),
    path(
        "categories/<pk>", category.CategoryUpdateView.as_view(), name="category_edit"
    ),
    path("content/pages/", content.PageListView.as_view(), name="page_list"),
    path("content/pages/new/", content.PageCreateView.as_view(), name="page_create"),
    path("content/pages/<pk>/", content.PageEditView.as_view(), name="page_edit"),
    path(
        "content/pages/<int:page_id>/copy/",
        content.PageCopyView.as_view(),
        name="page_copy",
    ),
    path(
        "content/pages/<int:page_id>/blocks/",
        content.PageBlockListView.as_view(),
        name="page_block_list",
    ),
    path(
        "content/pages/<int:page_id>/blocks/new/",
        content.PageBlockCreateView.as_view(),
        name="page_block_create",
    ),
    path(
        "content/pages/<int:page_id>/blocks/<int:pk>/",
        content.PageBlockUpdateView.as_view(),
        name="page_block_update",
    ),
    path(
        "content/pages/<int:page_id>/blocks/<int:pk>/settings/",
        content.PageBlockSettingsView.as_view(),
        name="page_block_settings",
    ),
    path(
        "content/pages/<int:page_id>/blocks/<int:pk>/delete/",
        content.PageBlockDeleteView.as_view(),
        name="page_block_delete",
    ),
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
        "content/menu/",
        content.MenuItemListView.as_view(),
        name="menu_list",
    ),
    path(
        "content/menu/edit/<pk>/",
        content.MenuItemUpdateView.as_view(),
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
    path("teams/export/", teams.TeamExportView.as_view(), name="team_export"),
    path("teams/create/", teams.TeamCreateView.as_view(), name="team_create"),
    path("teams/<int:pk>/", teams.TeamEditView.as_view(), name="team_edit"),
    path(
        "teams/recently_deleted",
        teams.RecentlyDeletedTeamsView.as_view(),
        name="recently_deleted",
    ),
    path(
        "teams/<int:pk>/tex_document/",
        teams.TeamGenerateDocumentView.as_view(),
        name="team_tex_document",
    ),
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
        "teams/<int:pk>/history/",
        teams.TeamHistoryView.as_view(),
        name="team_history",
    ),
    path(
        "teams/<int:pk>/delete/",
        teams.TeamDeleteView.as_view(),
        name="team_delete",
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
        "scanning/problems/undo/",
        scanning.UndoScanView.as_view(),
        name="scanning_problems_undo",
    ),
    path(
        "scanning/review/",
        scanning.VenueReviewView.as_view(),
        name="scanning_review",
    ),
    path(
        "scanning/review/<int:pk>/",
        scanning.TeamReviewView.as_view(),
        name="scanning_review_team",
    ),
    path(
        "scanning/review/<int:pk>/toggle/",
        scanning.TeamToggleReviewedView.as_view(),
        name="scanning_review_toggle_team",
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
    path("results/", results.ResultsHomeView.as_view(), name="results"),
    path(
        "results/announce/venue/<venue>/",
        results.VenueResultsAnnouncementView.as_view(),
        name="results_announce",
    ),
    path(
        "results/announce/country/<country>/<category>/",
        results.CountryResultsAnnouncementView.as_view(),
        name="results_announce_country",
    ),
    path("education/schools/", education.SchoolListView.as_view(), name="school_list"),
    path(
        "education/schools/<int:pk>/",
        education.SchoolUpdateView.as_view(),
        name="school_update",
    ),
    path(
        "education/schools/create/",
        education.SchoolCreateView.as_view(),
        name="school_create",
    ),
    path(
        "education/schools/import/",
        education.SchoolCSVImportView.as_view(),
        name="school_csv_import",
    ),
    path("gallery/albums/", album.AlbumListView.as_view(), name="album_list"),
    path("gallery/albums/new/", album.AlbumCreateView.as_view(), name="album_create"),
    path(
        "gallery/albums/<int:pk>/", album.AlbumUpdateView.as_view(), name="album_edit"
    ),
    path(
        "gallery/albums/<int:pk>/delete",
        album.AlbumDeleteView.as_view(),
        name="album_delete",
    ),
    path(
        "archive/import/",
        archive.ProblemImportView.as_view(),
        name="archive_import",
    ),
    path("venues/", include("bullet_admin.urls.venues")),
    path("files/", include("bullet_admin.urls.files")),
    path("wildcards/", include("bullet_admin.urls.wildcards")),
    path("documentation/", include("bullet_admin.urls.documentation")),
    path("tex/", include("bullet_admin.urls.tex")),
    path(
        "archive/problem_upload/",
        archive.ProblemPDFUploadView.as_view(),
        name="archive_problem_upload",
    ),
]
