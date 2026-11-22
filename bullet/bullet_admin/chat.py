"""Short-lived orgchat login tokens and competition-scoped channel grants."""

import base64
import hashlib
import hmac
import json
import time

from competitions.branches import Branches
from competitions.models import Competition, Venue
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.db.models import Q
from users.models import User

from bullet_admin.access import is_branch_admin, is_operator


def get_chat_channels(competition: Competition, user: User) -> list[dict[str, str]]:
    """Return explicit grants; operator roles never inherit country access."""
    if (
        not user.is_authenticated
        or not user.is_active
        or not is_operator(user, competition)
    ):
        raise PermissionDenied("You do not have chat access for this competition.")

    branch = Branches[competition.branch]
    prefix = branch.identifier[0]
    venues = Venue.objects.for_competition(competition)
    role = user.get_competition_role(competition)
    branch_admin = is_branch_admin(user, competition)
    countries = set()
    channels = {}

    if branch_admin:
        channels[f"{prefix}-global"] = f"{prefix}-global"
    elif role.is_operator:
        venues = venues.filter(pk__in=[venue.pk for venue in role.venues])
    else:
        countries.update(str(country) for country in role.countries or [])
        venues = venues.filter(
            Q(country__in=list(countries))
            | Q(pk__in=[venue.pk for venue in role.venues])
        )
        if countries:
            channels[f"{prefix}-global"] = f"{prefix}-global"

    for venue in venues:
        channel_id = f"{prefix}-{venue.shortcode}"
        channels[channel_id] = channel_id
        if not role.is_operator:
            countries.add(venue.country.code)

    for country in countries:
        channel_id = f"{prefix}-{country.upper()}"
        channels[channel_id] = channel_id

    return [
        {"id": channel_id, "name": channels[channel_id]}
        for channel_id in sorted(channels)
    ]


def get_chat_affiliation(competition: Competition, user: User) -> str:
    """Describe explicit permissions, rather than inherited channel access."""
    if is_branch_admin(user, competition):
        return "branch"

    role = user.get_competition_role(competition)
    suffix = "~" if role.is_operator else ""
    affiliations = {f"{venue.shortcode}{suffix}" for venue in role.venues}
    if not role.is_operator:
        affiliations.update(str(country).upper() for country in role.countries or [])
    return ",".join(sorted(affiliations))


def _encode_json(value) -> bytes:
    raw = json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return base64.urlsafe_b64encode(raw).rstrip(b"=")


def generate_chat_login_jwt(competition: Competition, user: User) -> str:
    """Issue an HS256 login JWT valid for 60 seconds, not a chat session token."""
    channels = get_chat_channels(competition, user)
    secret = settings.ORGCHAT_JWT_SECRET.encode("utf-8")
    if len(secret) < 32:
        raise ImproperlyConfigured("ORGCHAT_JWT_SECRET must contain at least 32 bytes.")
    if len(channels) > 256:
        raise ImproperlyConfigured("Orgchat supports at most 256 channels per user.")

    branch = Branches[competition.branch]
    user_id = str(user.pk * 10 + branch.id)
    username = user.get_full_name().strip() or user.email.partition("@")[0]
    # Orgchat limits profile strings to 256 UTF-8 bytes.
    username = username.encode("utf-8")[:256].decode("utf-8", errors="ignore")
    now = int(time.time())
    claims = {
        "sub": user_id,
        "iat": now,
        "exp": now + 60,
        "admin": is_branch_admin(user, competition),
        "user": {
            "id": user_id,
            "username": username,
            "affiliation": get_chat_affiliation(competition, user),
        },
        "channels": channels,
    }

    signing_input = b".".join(
        [_encode_json({"alg": "HS256", "typ": "JWT"}), _encode_json(claims)]
    )
    signature = hmac.new(secret, signing_input, hashlib.sha256).digest()
    token = signing_input + b"." + base64.urlsafe_b64encode(signature).rstrip(b"=")
    if len(token) > 16384:
        raise ImproperlyConfigured("Orgchat login JWT exceeds the 16 KiB limit.")
    return token.decode("ascii")
