import dns.exception
import dns.resolver
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_email_mx_record(email: str):
    domain_name = email.rsplit("@", 1)[-1]
    try:
        dns.resolver.resolve(domain_name, "MX")
    except (
        dns.resolver.NXDOMAIN,
        dns.resolver.NoAnswer,
        dns.resolver.NoNameservers,
        dns.exception.Timeout,
    ):
        raise ValidationError(_("Invalid email address."))
