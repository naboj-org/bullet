import json

from django.core.management import BaseCommand
from django.db import transaction

from users.models import User


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **kwargs):
        j = json.load(open('naboj_user.json'))

        for old_user in j:
            split_names = old_user['full_name'].split(' ')
            if len(split_names) == 1:
                split_names = [''] + split_names
            first_name, last_name = split_names[:2]
            User.objects.create(
                first_name=first_name,
                last_name=last_name,
                username=old_user["login"],
                email=old_user["email"] if old_user["email"] != "" else None,
                is_staff=True,
                is_active=True,
                password=f"md5${old_user['salt']}${old_user['password']}"
            )
