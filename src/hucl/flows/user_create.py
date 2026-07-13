import urllib.request
import urllib.parse
import json
import logging

from .shared import APIUrl
from ..drivers.sansio import SansioImpl

logger = logging.getLogger(__name__)


def create_user_sansio(
    *, api_url: APIUrl, api_token: str, user_name: str = None, admin: bool = False
) -> SansioImpl:
    """
    Basic reconciliation loop for creating a user on a JupyterHub.
    Existing servers with the same name (or default, not given) will be re-used.

    :param api_url: URL for JupyterHub API endpoint
    """
    auth_headers = {"Authorization": f"token {api_token}"}

    # Get current user
    resp = yield urllib.request.Request(
        f"{api_url}/users/{user_name}", headers=auth_headers, method="POST"
    )
    if resp.status == 409:
        return

    if resp.status != 201:
        raise RuntimeError("Expected HTTP 201 Created for newly created user")

    # Get current user
    resp = yield urllib.request.Request(
        f"{api_url}/users/{user_name}",
        data=json.dumps({"admin": admin}).encode("utf-8"),
        headers=auth_headers,
        method="POST",
    )

    if resp.status == 200:
        RuntimeError("Expected HTTP 200 OK for modified user")
