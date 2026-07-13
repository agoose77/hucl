import urllib.request
import urllib.parse
import contextlib
import logging
import time

from .sansio import SansioImpl, Sleep, Read, ReadLine, Close, NetworkResponse

logger = logging.getLogger(__name__)


def sync_driver(loop: SansioImpl):
    response = None
    with contextlib.ExitStack() as stack:
        while True:
            logger.debug(f"Send event response: {type(response)}")
            try:
                request = loop.send(response)
            except StopIteration as err:
                return err.value
            logger.debug(f"Receive event: {type(request)}")

            response = None
            match request:
                case Sleep(duration_s):
                    time.sleep(duration_s)
                case Read(readable):
                    assert isinstance(readable, NetworkResponse)
                    response = readable._impl.read()
                case ReadLine(readable):
                    assert isinstance(readable, NetworkResponse)
                    response = readable._impl.readline()
                case Close(closable):
                    assert isinstance(closable, NetworkResponse)
                    closable._impl.close()
                case urllib.request.Request():
                    print(request.get_full_url())
                    f = stack.enter_context(urllib.request.urlopen(request))
                    response = NetworkResponse(f.status, f.headers, f)
