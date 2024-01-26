from competitions.models import Competition


def competition_timeline_context(request, data):
    data["competition"] = Competition.objects.get_current_competition(request.BRANCH)
    return data
