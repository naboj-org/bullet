from django.contrib import admin

from competitions.models import Competition, CategoryCompetition, Site, CompetitionSite, Problem, CompetitionProblem, \
    LocalizedProblem, SolutionSubmitLog, Wildcard


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    pass


@admin.register(CategoryCompetition)
class CategoryCompetitionAdmin(admin.ModelAdmin):
    pass


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    pass


@admin.register(CompetitionSite)
class CompetitionSiteAdmin(admin.ModelAdmin):
    pass


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    pass


@admin.register(CompetitionProblem)
class CompetitionProblemAdmin(admin.ModelAdmin):
    pass


@admin.register(LocalizedProblem)
class LocalizedProblemAdmin(admin.ModelAdmin):
    pass


@admin.register(SolutionSubmitLog)
class SolutionSubmitLogAdmin(admin.ModelAdmin):
    pass


@admin.register(Wildcard)
class WildcardAdmin(admin.ModelAdmin):
    pass
