from django.urls import path

from bullet_admin.views import venues

urlpatterns = [
    path("", venues.VenueListView.as_view(), name="venue_list"),
    path("create/", venues.VenueCreateView.as_view(), name="venue_create"),
    path("<int:pk>/", venues.VenueDetailView.as_view(), name="venue_detail"),
    path("<int:pk>/edit/", venues.VenueUpdateView.as_view(), name="venue_update"),
    path(
        "<int:pk>/waiting_list/", venues.WaitingListView.as_view(), name="waiting_list"
    ),
    path(
        "<int:pk>/waiting_list/automove/",
        venues.WaitingListAutomoveView.as_view(),
        name="waiting_list_automove",
    ),
    path(
        "<int:pk>/certificates/",
        venues.CertificateView.as_view(),
        name="venue_certificates",
    ),
    path(
        "<int:pk>/team_lists/",
        venues.TeamListView.as_view(),
        name="venue_teamlists",
    ),
    path(
        "<int:pk>/tearoffs/",
        venues.TearoffView.as_view(),
        name="venue_tearoffs",
    ),
]
