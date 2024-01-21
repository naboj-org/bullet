from django.contrib import admin
from django.db.models import ManyToManyField
from django.forms import CheckboxSelectMultiple

from education.models import Education, Grade, School, SchoolType


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "country")
    search_fields = ("name", "search", "country")


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
        x = []
        last_school = None
        from_this = []

        for grade in obj.grades.all():
            if last_school is not None and last_school != grade.school_type:
                x.append(f"{last_school.name} ({', '.join(from_this)})")
                from_this.clear()
            last_school = grade.school_type
            from_this.append(grade.name)

        if len(from_this):
            x.append(f"{last_school.name} ({', '.join(from_this)})")

        return ", ".join(x)
