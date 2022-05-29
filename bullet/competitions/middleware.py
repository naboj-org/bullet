from competitions.branches import Branches
from django.http import HttpResponseForbidden


class BranchMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        branch = Branches.get_from_domain(request.get_host())
        if branch is None:
            return HttpResponseForbidden("Unknown branch.")

        request.BRANCH = branch

        response = self.get_response(request)
        return response
