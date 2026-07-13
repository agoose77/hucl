import asyncio
import contextlib
import urllib.request
import urllib.parse
import logging

from .sansio import SansioImpl, Sleep, Read, ReadLine, Close, NetworkResponse

logger = logging.getLogger(__name__)


async def async_driver(loop: SansioImpl):
    import aiohttp.client

    async with aiohttp.ClientSession() as session, contextlib.AsyncExitStack() as stack:
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
                    await asyncio.sleep(duration_s)
                case Read(readable):
                    assert isinstance(readable, NetworkResponse)
                    response = await readable._impl.content.read()
                case ReadLine(readable):
                    assert isinstance(readable, NetworkResponse)
                    response = await readable._impl.content.readline()
                case Close(closable):
                    assert isinstance(readable._impl, NetworkResponse)
                    closable.close()
                case urllib.request.Request():
                    resp = await stack.enter_async_context(
                        session.request(
                            request.get_method(),
                            request.get_full_url(),
                            headers=dict(request.header_items()),
                            data=request.data,
                        )
                    )
                    response = NetworkResponse(resp.status, resp.headers, resp)
