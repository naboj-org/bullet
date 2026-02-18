from bullet_admin.csv_import import (
    SchoolCSVImporter,
    send_import_result_email,
)
from django.core.files.base import File
from django.core.files.storage import default_storage
from django_rq import job

from education.models import School


@job
def send_schools_to_search(school_ids: list[int]):
    schools = School.objects.filter(id__in=school_ids)
    for school in schools:
        school.send_to_search()


@job
def import_schools_async(file_path: str, country: str, user_email: str):
    file_obj = open(default_storage.path(file_path), "rb")
    django_file = File(file_obj, name=file_path.split("/")[-1])

    importer = SchoolCSVImporter(
        csv_file=django_file,
        country=country,
    )

    try:
        result = importer.import_schools()
        send_import_result_email(user_email, result)
    except Exception as e:
        error_result = {
            "created": 0,
            "updated": 0,
            "errors": [str(e)],
            "total": 0,
        }
        send_import_result_email(user_email, error_result)
    finally:
        file_obj.close()

        if default_storage.exists(file_path):
            default_storage.delete(file_path)
