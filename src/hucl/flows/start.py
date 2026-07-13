import urllib.request
import urllib.parse
import json
import random
import enum
import logging

from .shared import APIUrl
from ..drivers.sansio import SansioImpl, Read, ReadLine, Sleep

logger = logging.getLogger(__name__)

DATA_PREFIX = b"data: "
RANDOM_REQUESTS_PER_MIN = 10


class State(enum.StrEnum):
    check_status = enum.auto()
    start_server = enum.auto()
    wait_for_start = enum.auto()
    wait_for_stop = enum.auto()


def get_user_api_url(api_url: APIUrl, user_name: str | None) -> str:
    user_path = "/user" if user_name is None else f"/users/{user_name}"
    return f"{api_url}{user_path}"


def get_server_api_url(api_url: APIUrl, user_name: str, server_name: str | None) -> str:
    server_path = "/server" if server_name is None else f"/servers/{server_name}"
    return f"{api_url}/users/{user_name}{server_path}"


def start_server_sansio(
    api_url: APIUrl,
    api_token: str,
    user_name: str = None,
    server_name: str = None,
    profile_options: dict[str, str] = None,
) -> SansioImpl:
    """
    Basic reconciliation loop for starting a (named) server on a JupyterHub.
    Existing servers with the same name (or default, not given) will be re-used.

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
                resp = yield urllib.request.Request(
                    get_user_api_url(api_url, user_name), headers=auth_headers
                )
                content = yield Read(resp)

                user_model = json.loads(content)

                # Is the server known of?
                existing_server = user_model["servers"].get(server_name or "")
                resolved_user_name = user_model["name"]

                # Transition
                match existing_server:
                    case None:
                        state = State.start_server
                    case {"pending": "start", **rest}:
                        state = State.wait_for_start
                    case {"pending": "stop", **rest}:
                        state = State.wait_for_stop
                    case _:
                        assert existing_server["ready"]
                        return existing_server["url"]

            case State.start_server:
                # Try to start server
                resp = yield urllib.request.Request(
                    get_server_api_url(api_url, resolved_user_name, server_name),
                    method="POST",
                    data=json.dumps(
                        {} if profile_options is None else profile_options
                    ).encode("utf-8"),
                    headers={**auth_headers, "Content-Type": "application/json"},
                )

                # Handle response
                match resp.status:
                    # Server already running
                    case 201:
                        state = State.check_status
                    case 202:
                        state = State.wait_for_start
                    case 429:
                        retry_after = resp.headers.get("Retry-After")
                        delay = (
                            random.expovariate(RANDOM_REQUESTS_PER_MIN / 60)
                            if retry_after is None
                            else float(retry_after)
                        )
                        logger.info(
                            f"Server asked us to back off, waiting for {delay:.1f} seconds"
                        )
                        yield Sleep(delay)
                    case _:
                        raise RuntimeError(resp.status)

            case State.wait_for_start:
                # Get URL
                resp = yield (
                    urllib.request.Request(
                        f"{get_server_api_url(api_url, resolved_user_name, server_name)}/progress",
                        method="GET",
                        headers=auth_headers,
                    )
                )
                while True:
                    line = yield ReadLine(resp)
                    if not line.startswith(DATA_PREFIX):
                        continue

                    logger.debug(line.decode())

                    # Load JSON response line
                    line_data = json.loads(line[len(DATA_PREFIX) :].decode())
                    if line_data.get("ready"):
                        return line_data["url"]

            case State.wait_for_stop:
                delay = random.expovariate(RANDOM_REQUESTS_PER_MIN / 60)
                logger.info(f"Waiting for server to stop for {delay:.1f} seconds")
                yield Sleep(delay)
                state = State.check_status
