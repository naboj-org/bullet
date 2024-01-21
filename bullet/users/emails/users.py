from django_rq import job

from bullet.utils.email import send_email
from users.models import User


@job
def send_onboarding_email(branch, user_id: int, password):
    user = User.objects.get(id=user_id)
    send_email(
        branch,
        user.email,
        "Your new admin account for Náboj",
        "mail/messages/new_user.html",
        "mail/messages/new_user.txt",
        {"user": user, "password": password},
    )
