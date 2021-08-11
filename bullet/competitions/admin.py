from django.contrib import admin

from competitions.models import Competition, CategoryCompetition, Site, CompetitionSite, Problem, CompetitionProblem, \
    LocalizedProblem, SolutionSubmitLog, Wildcard


class CategoryCompetitionInlineAdmin(admin.TabularInline):
    extra = 0
    model = CategoryCompetition


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    inlines = (CategoryCompetitionInlineAdmin, )
    list_display = ('name', 'branch', 'registration_start', 'registration_end', 'competition_start')


class CompetitionSiteInlineAdmin(admin.TabularInline):
    model = CompetitionSite
    extra = 0


@admin.register(CategoryCompetition)
class CategoryCompetitionAdmin(admin.ModelAdmin):
    inlines = (CompetitionSiteInlineAdmin, )
    list_display = ('competition', 'category', 'problems_per_team', 'max_teams_per_school', 'max_members_per_team', 'ranking')


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'address')


@admin.register(CompetitionSite)
class CompetitionSiteAdmin(admin.ModelAdmin):
    list_display = ('site', 'category_competition', 'capacity', 'accepted_languages', 'local_start')


class LocalizedProblemInlineAdmin(admin.TabularInline):
    model = LocalizedProblem
    extra = 0


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    inlines = (LocalizedProblemInlineAdmin, )


@admin.register(CompetitionProblem)
class CompetitionProblemAdmin(admin.ModelAdmin):
    list_display = ('problem', 'category_competition', 'number')


@admin.register(LocalizedProblem)
class LocalizedProblemAdmin(admin.ModelAdmin):
    list_display = ('problem', 'language')


@admin.register(SolutionSubmitLog)
class SolutionSubmitLogAdmin(admin.ModelAdmin):
    pass


@admin.register(Wildcard)
class WildcardAdmin(admin.ModelAdmin):
    pass
