from typing import cast, NewType

type APIUrl = NewType("APIUrl", str)


def ensure_api_url(maybe_url: str) -> APIUrl:
    return cast(APIUrl, maybe_url.rstrip("/"))
