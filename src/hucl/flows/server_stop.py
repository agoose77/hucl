import urllib.request
import urllib.parse
import json
import random
import enum
import logging

from .shared import APIUrl, flow
from ..sansio import SansioImpl, read, sleep, network_request
from typing import Optional

logger = logging.getLogger(__name__)

RANDOM_REQUESTS_PER_MIN = 10


class State(enum.StrEnum):
    check_status = enum.auto()
    stop_server = enum.auto()
    wait_for_stop = enum.auto()


def get_user_api_url(api_url: APIUrl, user_name: str | None) -> str:
    user_path = "/user" if user_name is None else f"/users/{user_name}"
    return f"{api_url}{user_path}"


def get_server_api_url(api_url: APIUrl, user_name: str, server_name: str | None) -> str:
    server_path = "/server" if server_name is None else f"/servers/{server_name}"
    return f"{api_url}/users/{user_name}{server_path}"


@flow
def stop_server_sansio(
    *,
    api_url: APIUrl,
    api_token: str,
    user_name: Optional[str] = None,
    server_name: Optional[str] = None,
    remove: bool = False,
) -> SansioImpl:
    """
    Basic reconciliation loop for stopping a (named) server on a JupyterHub.

    :param api_url: URL for JupyterHub API endpoint
    """
    auth_headers = {"Authorization": f"token {api_token}"}

    # Initial state
    state = State.check_status

    # State data (side effects)
    resolved_user_name: str

    while True:
        logger.debug(state)
        match state:
            case State.check_status:
                # Get current user
                resp = yield from network_request(
                    urllib.request.Request(
                        get_user_api_url(api_url, user_name), headers=auth_headers
                    )
                )
                content = yield from read(resp)

                user_model = json.loads(content)

                # Is the server known of?
                existing_server = user_model["servers"].get(server_name or "")
                resolved_user_name = user_model["name"]

                # Transition
                match existing_server:
                    # Doesn't exist
                    case None:
                        # Done
                        return
                    case {"pending": "stop", **rest}:
                        state = State.wait_for_stop
                    case _:
                        # Running
                        state = State.stop_server

            case State.stop_server:
                # Try to start server
                resp = yield from network_request(
                    urllib.request.Request(
                        get_server_api_url(api_url, resolved_user_name, server_name),
                        method="DELETE",
                        data=json.dumps(
                            {"remove": remove and server_name is not None}
                        ).encode("utf-8"),
                        headers={**auth_headers, "Content-Type": "application/json"},
                    )
                )  # Handle response
                match resp.status:
                    # Server already running
                    case 202:
                        # Server stopping
                        state = State.wait_for_stop
                    case 204:
                        # Server already stopped (but not removed)
                        return
                    case _:
                        raise RuntimeError(resp.status)

            case State.wait_for_stop:
                delay = random.expovariate(RANDOM_REQUESTS_PER_MIN / 60)
                logger.info(f"Waiting for server to stop for {delay:.1f} seconds")
                yield from sleep(delay)
                state = State.check_status
