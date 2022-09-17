from django.http import HttpResponseNotAllowed
from django.views.generic.edit import BaseDeleteView


class DeleteView(BaseDeleteView):
    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(permitted_methods=["POST"])
