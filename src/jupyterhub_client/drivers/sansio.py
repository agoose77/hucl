import dataclasses
import urllib.request

from typing import Any, Generator


@dataclasses.dataclass
class Read:
    readable: Any


@dataclasses.dataclass
class ReadLine:
    readable: Any


@dataclasses.dataclass
class Close:
    closable: Any


@dataclasses.dataclass
class Sleep:
    duration_s: Any


@dataclasses.dataclass
class NetworkResponse:
    status: int
    headers: dict
    _impl: Any


type Request = Sleep | Read | ReadLine | Close | urllib.request.Request
type Response = bytes | bytearray | NetworkResponse | None
type SansioImpl = Generator[Request, Response, str]
