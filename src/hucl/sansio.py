import dataclasses
import urllib.request

from typing import overload, Generator, Any


@dataclasses.dataclass
class NetworkResponse:
    status: int
    headers: dict
    _impl: Any


@dataclasses.dataclass
class Read:
    readable: NetworkResponse


@dataclasses.dataclass
class ReadLine:
    readable: NetworkResponse


@dataclasses.dataclass
class Close:
    closable: NetworkResponse


@dataclasses.dataclass
class Sleep:
    duration_s: float


type Request = Sleep | Read | ReadLine | Close | urllib.request.Request
type Response = bytes | bytearray | NetworkResponse | None
type SansioImpl[T] = Generator[Request, Response, T]

type IODispatcher[Req, Resp] = Generator[Req, Resp, Resp]


def sleep(duration_s: float) -> IODispatcher[Sleep, None]:
    return (yield Sleep(duration_s))


def read(response: NetworkResponse) -> IODispatcher[Read, bytes | bytearray]:
    return (yield Read(response))


def close(response: NetworkResponse) -> IODispatcher[Close, None]:
    return (yield Close(response))


def read_line(
    response: NetworkResponse,
) -> IODispatcher[ReadLine, bytes | bytearray]:
    return (yield ReadLine(response))


def network_request(
    request: urllib.request.Request,
) -> IODispatcher[urllib.request.Request, NetworkResponse]:
    return (yield request)
