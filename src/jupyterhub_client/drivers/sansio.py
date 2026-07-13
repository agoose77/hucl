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


type Request = Sleep | Read | ReadLine | Close | urllib.request.Request
type Response = bytes | bytearray | None
type StateMachineType = Generator[Request, Response, str]
