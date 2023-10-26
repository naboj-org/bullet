from bullet_admin.access import SchoolEditorAccess
from bullet_admin.forms.education import SchoolForm
from bullet_admin.views import GenericForm
from django.shortcuts import redirect
from django.views.generic import CreateView, ListView, UpdateView
from education.models import School

from bullet import search


class SchoolQuerySetMixin:
    def get_queryset(self):
        return School.objects.filter(is_legacy=False)


class SchoolListView(SchoolEditorAccess, SchoolQuerySetMixin, ListView):
    template_name = "bullet_admin/education/school_list.html"
    paginate_by = 100

    def get_queryset(self):
        qs = super().get_queryset()
        search_query = self.request.GET.get("q")
        if search_query:
            ids = search.client.index("schools").search(search_query)["hits"]
            ids = [x["id"] for x in ids]
            qs = qs.filter(id__in=ids).all()
            qs = sorted(qs, key=lambda s: ids.index(s.id))
        else:
            qs = qs.order_by("country", "name", "address")
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)
        ctx["school_count"] = School.objects.count()
        return ctx


class SchoolUpdateView(
    SchoolEditorAccess, SchoolQuerySetMixin, GenericForm, UpdateView
):
    form_class = SchoolForm
    template_name = "bullet_admin/education/school_form.html"
    form_title = "Edit school"

    def form_valid(self, form):
        school: School = form.save(commit=False)
        school.importer_ignored = True
        school.save()
        form.save_m2m()

        return redirect("badmin:school_list")


class SchoolCreateView(
    SchoolEditorAccess, SchoolQuerySetMixin, GenericForm, CreateView
):
    form_class = SchoolForm
    form_title = "New school"

    def form_valid(self, form):
        school: School = form.save(commit=False)
        school.importer_ignored = True
        school.save()
        form.save_m2m()

        return redirect("badmin:school_list")
