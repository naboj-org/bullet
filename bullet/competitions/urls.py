from competitions.views import archive, live, register, teams
from django.urls import path

urlpatterns = [
    path(
        "register/",
        register.CategorySelectView.as_view(),
        name="register",
    ),
    path(
        "register/venue/",
        register.VenueSelectView.as_view(),
        name="register_venue",
    ),
    path(
        "register/school/",
        register.SchoolSelectView.as_view(),
        name="register_school",
    ),
    path(
        "register/details/",
        register.TeamDetailsView.as_view(),
        name="register_details",
    ),
    path(
        "register/thanks/",
        register.ThanksView.as_view(),
        name="register_thanks",
    ),
    path("teams/", teams.TeamListView.as_view(), name="team_list"),
    path("teams/waiting/", teams.WaitingListView.as_view(), name="waiting_list"),
    path("teams/<secret_link>/", teams.TeamEditView.as_view(), name="team_edit"),
    path(
        "teams/<secret_link>/unregister/",
        teams.TeamDeleteView.as_view(),
        name="team_delete",
    ),
    path(
        "teams/<secret_link>/certificate/",
        teams.TeamCertificateView.as_view(),
        name="team_certificate",
    ),
    path("live/", live.LiveView.as_view(), name="live"),
    path("live/countdown/", live.LiveCountdownView.as_view(), name="live_countdown"),
    path("live/results/", live.LiveResultsView.as_view(), name="live_results"),
    path(
        "live/first_problem/",
        live.LiveFirstProblemView.as_view(),
        name="live_first_problem",
    ),
    path("archive/", archive.ArchiveListView.as_view(), name="archive"),
]
