from django.http import HttpResponseRedirect


class FormAndFormsetMixin:
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["formset"] = self.get_formset()
        return ctx

    def get_formset_class(self):
        raise NotImplementedError()

    def get_formset(self):
        return self.get_formset_class()(**self.get_formset_kwargs())

    def get_formset_kwargs(self):
        kwargs = {}
        if self.request.method in ("POST", "PUT"):
            kwargs.update(
                {
                    "data": self.request.POST,
                    "files": self.request.FILES,
                }
            )
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        formset = self.get_formset()

        if form.is_valid() and formset.is_valid():
            return self.forms_valid(form, formset)
        else:
            return self.form_invalid(form)

    def save_forms(self, form, formset):
        form.save()
        formset.save()

    def forms_valid(self, form, formset):
        self.save_forms(form, formset)
        return HttpResponseRedirect(self.get_success_url())
