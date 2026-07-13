import urllib.request
import urllib.parse
import logging
import time

from .sansio import StateMachineType, Sleep, Read, ReadLine, Close

logger = logging.getLogger(__name__)


def sync_driver(loop: StateMachineType):
    response = None
    while True:
        logger.debug("Send event response", response)
        try:
            request = loop.send(response)
        except StopIteration as err:
            return err.value
        logger.debug("Receive event", request)

        response = None
        match request:
            case Sleep(duration_s):
                time.sleep(duration_s)
            case Read(readable):
                response = readable.read()
            case Close(closable):
                closable.close()
            case ReadLine(readable):
                response = readable.readline()
            case urllib.request.Request():
                f = urllib.request.urlopen(request)
                response = (f.status, f)
