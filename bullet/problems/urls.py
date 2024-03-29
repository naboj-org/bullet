from django.urls import path

from problems.views import archive, results

urlpatterns = [
    path(
        "results/",
        results.ResultsSelectView.as_view(),
        name="results",
    ),
    path(
        "results/category/<category>/",
        results.CategoryResultsView.as_view(),
        name="results_category",
    ),
    path(
        "results/category/<category>/country/<country>/",
        results.CategoryResultsView.as_view(),
        name="results_category",
    ),
    path(
        "results/venue/<venue>/",
        results.VenueResultsView.as_view(),
        name="results_venue",
    ),
    path(
        "archive/<int:competition_number>/results/",
        archive.ArchiveResultsSelectView.as_view(),
        name="archive_results",
    ),
    path(
        "archive/<int:competition_number>/results/category/<category>/",
        archive.ArchiveCategoryResultsView.as_view(),
        name="archive_results_category",
    ),
    path(
        "archive/<int:competition_number>/results/category/<category>"
        "/country/<country>/",
        archive.ArchiveCategoryResultsView.as_view(),
        name="archive_results_category",
    ),
    path(
        "archive/<int:competition_number>/results/venue/<venue>/",
        archive.ArchiveVenueResultsView.as_view(),
        name="archive_results_venue",
    ),
    path(
        "archive/<int:competition_number>/problems/",
        archive.ProblemStatementView.as_view(),
        name="archive_problems",
    ),
]
