from django.contrib import admin
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

    def grade_list(self, obj):
        return ", ".join([x.name for x in obj.grades.all()])
