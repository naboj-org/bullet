from bullet import VERSION


def branch_context(request):
    if not hasattr(request, "BRANCH"):
        return {}

    return {
        "branch": request.BRANCH,
    }


def version_context(request):
    return {
        "bullet_version": VERSION,
    }
