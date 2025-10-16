from django_rq import job

from education.models import School


@job
def send_schools_to_search(school_ids: list[int]):
    schools = School.objects.filter(id__in=school_ids)
    for school in schools:
        school.send_to_search()
