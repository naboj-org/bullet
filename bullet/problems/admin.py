from django.contrib import admin

from problems import models


class ProblemStatementInline(admin.StackedInline):
    model = models.ProblemStatement


@admin.register(models.Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_filter = ("competition", "competition__branch")
    list_display = ("number", "competition")
    inlines = (ProblemStatementInline,)


@admin.register(models.ProblemStatement)
class ProblemStatementAdmin(admin.ModelAdmin):
    list_display = ("problem", "language")
