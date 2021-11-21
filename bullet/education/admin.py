from django.contrib import admin
from django.db.models import ManyToManyField
from django.forms import CheckboxSelectMultiple
from education.models import Education, Grade, School, SchoolType


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "izo")


class GradeInline(admin.TabularInline):
    model = Grade


@admin.register(SchoolType)
class SchoolTypeAdmin(admin.ModelAdmin):
    inlines = [GradeInline]


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ("name", "grade_list")
    formfield_overrides = {ManyToManyField: {"widget": CheckboxSelectMultiple()}}

    def grade_list(self, obj):
        return ", ".join([str(x) for x in obj.grades.all()])
