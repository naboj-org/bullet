from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template


def send_email(branch, to, subject, template, text_template, context, reply_to=None):
    context["branch"] = branch
    context["root_url"] = f"https://{branch.identifier}.{settings.PARENT_HOST}"
    context["subject"] = subject
    html_content = get_template(template).render(context)
    text_content = get_template(text_template).render(context)
    msg = EmailMultiAlternatives(
        subject, text_content, settings.DEFAULT_FROM_EMAIL, [to]
    )
    if reply_to:
        msg.reply_to = reply_to
    msg.attach_alternative(html_content, "text/html")
    msg.send()
