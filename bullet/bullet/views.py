from django.http import HttpResponseRedirect


class FormAndFormsetMixin:
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if "formset" not in kwargs:
            ctx["formset"] = self.get_formset()
        return ctx

    def get_formset_class(self):
        raise NotImplementedError()

    def get_formset(self):
        cls = self.get_formset_class()
        if cls is None:
            return None
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

        if formset is None:
            if form.is_valid():
                return self.forms_valid(form, None)
            else:
                return self.forms_invalid(form, formset)

        if form.is_valid() and formset.is_valid():
            return self.forms_valid(form, formset)
        else:
            return self.forms_invalid(form, formset)

    def save_forms(self, form, formset):
        form.save()
        formset.save()

    def forms_valid(self, form, formset):
        self.save_forms(form, formset)
        return HttpResponseRedirect(self.get_success_url())

    def forms_invalid(self, form, formset):
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset)
        )
