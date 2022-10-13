from bullet.utils.email import send_email


def send_onboarding_email(branch, user, password):
    send_email(
        branch,
        user.email,
        "Your new admin account for Náboj",
        "mail/messages/new_user.txt",
        "mail/messages/new_user.txt",
        {"user": user, "password": password},
    )
