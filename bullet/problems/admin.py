from django.contrib import admin

from problems import models


class CategoryProblemAdminInline(admin.TabularInline):
    model = models.CategoryProblem


@admin.register(models.Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_filter = ("competition", "competition__branch")
    list_display = ("name", "competition")
    inlines = (CategoryProblemAdminInline,)


@admin.register(models.ProblemStatement)
class ProblemStatementAdmin(admin.ModelAdmin):
    list_display = ("problem", "language")
