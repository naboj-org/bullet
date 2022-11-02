from django.urls import path
from problems import views

urlpatterns = [
    path(
        "results/",
        views.ResultsSelectView.as_view(),
        name="results",
    ),
    path(
        "results/category/<category>/",
        views.CategoryResultsView.as_view(),
        name="results_category",
    ),
    path(
        "results/category/<category>/country/<country>/",
        views.CategoryResultsView.as_view(),
        name="results_category",
    ),
    path(
        "results/venue/<venue>/",
        views.VenueResultsView.as_view(),
        name="results_venue",
    ),
]
