from competitions.views import register, teams
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
]
