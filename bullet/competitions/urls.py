from competitions.views import register
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
]
