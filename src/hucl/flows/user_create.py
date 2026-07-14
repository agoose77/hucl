import urllib.request
import urllib.parse
import json
import logging

from .shared import APIUrl, flow
from ..sansio import SansioImpl, network_request

logger = logging.getLogger(__name__)


@flow
def create_user(
    *, api_url: APIUrl, api_token: str, user_name: str, admin: bool = False
) -> SansioImpl:
    """
    Basic reconciliation loop for creating a user on a JupyterHub.
    Existing servers with the same name (or default, not given) will be re-used.

    :param api_url: URL for JupyterHub API endpoint
    """
    auth_headers = {"Authorization": f"token {api_token}"}

    # Get current user
    resp = yield from network_request(
        urllib.request.Request(
            f"{api_url}/users/{user_name}", headers=auth_headers, method="POST"
        )
    )
    if resp.status == 409:
        return

    if resp.status != 201:
        raise RuntimeError("Expected HTTP 201 Created for newly created user")

    if admin:
        # Get current user
        resp = yield from network_request(
            urllib.request.Request(
                f"{api_url}/users/{user_name}",
                data=json.dumps({"admin": True}).encode("utf-8"),
                headers=auth_headers,
                method="PATCH",
            )
        )

        if resp.status != 200:
            RuntimeError("Expected HTTP 200 OK for modified user")
