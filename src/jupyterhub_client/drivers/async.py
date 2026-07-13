import asyncio
import contextlib
import urllib.request
import urllib.parse
import logging

from .sansio import StateMachineType, Sleep, Read, ReadLine, Close

logger = logging.getLogger(__name__)


async def async_driver(loop: StateMachineType):
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
                    assert isinstance(readable, aiohttp.client.ClientResponse)
                    response = await readable.content.read()
                case ReadLine(readable):
                    assert isinstance(readable, aiohttp.client.ClientResponse)
                    response = await readable.content.readline()
                case Close(closable):
                    assert isinstance(readable, aiohttp.client.ClientResponse)
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
                    response = (resp.status, resp)
