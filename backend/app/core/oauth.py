from enum import Enum
from typing import Any


class OAuthProvider(str, Enum):
    GOOGLE = "google"
    GITHUB = "github"


class OAuthClientConfig:
    """Placeholder for Authlib client configuration.

    In V1 we keep this minimal and wire full Authlib integration later.
    """

    def __init__(self, name: str, client_id: str, client_secret: str, redirect_uri: str) -> None:
        self.name = name
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri


def build_oauth_state(provider: OAuthProvider) -> str:
    # TODO: implement state generation + CSRF protection
    return f"state-{provider.value}"


def parse_oauth_userinfo(provider: OAuthProvider, raw_data: dict[str, Any]) -> dict[str, Any]:
    """Normalize provider-specific user info to a common shape.

    This is a placeholder; actual mapping depends on Authlib responses.
    """

    return {"provider": provider.value, "raw": raw_data}
