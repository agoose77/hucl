import urllib.reques
import urllib.parse
import json
import logging

from .shared import APIUrl
from ..drivers.sansio import SansioImpl

logger = logging.getLogger(__name__)


def delete_user_sansio(
    *, api_url: APIUrl, api_token: str, user_name: str = None, admin: bool = False
) -> SansioImpl:
    """
    Basic reconciliation loop for deleting a user on a JupyterHub.
    Existing servers with the same name (or default, not given) will be re-used.

    :param api_url: URL for JupyterHub API endpoint
    """
    auth_headers = {"Authorization": f"token {api_token}"}

    # Get current user
    resp = yield urllib.request.Request(
        f"{api_url}/users/{user_name}", headers=auth_headers, method="DELETE"
    )
    if resp.status != 204:
        raise RuntimeError("Expected HTTP 201 Created for newly created user")
