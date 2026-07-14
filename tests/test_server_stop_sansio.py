from hucl.flows.server_stop import stop_server_sansio
from hucl.sansio import Read, NetworkResponse, Sleep
import urllib.request
import json
import pytest


@pytest.fixture
def flow():
    return stop_server_sansio(
        api_url="http://my-hub.com/hub/api", api_token="123456-a-token"
    )


def test_unnamed_running_fast_stop(flow):
    # First, it should request the user model
    request = flow.send(None)
    assert isinstance(request, urllib.request.Request)
    assert request.get_full_url() == "http://my-hub.com/hub/api/user"
    assert request.get_method() == "GET"

    # We send our 200 response and then a token
    response = NetworkResponse(200, {}, object())
    request = flow.send(response)

    # Ensure it's reading this obj
    assert isinstance(request, Read)
    assert request.readable is response

    # Ensure that we get the proper result!
    request = flow.send(
        json.dumps(
            {"name": "bob", "servers": {"": {"ready": True, "url": "/user/bob"}}}
        ).encode("utf-8")
    )
    assert isinstance(request, urllib.request.Request)
    assert request.get_full_url() == "http://my-hub.com/hub/api/users/bob/server"
    assert request.get_method() == "DELETE"

    # We send our 200 response and then a token
    response = NetworkResponse(204, {}, object())

    with pytest.raises(StopIteration):
        flow.send(response)


def test_unnamed_running_slow_stop(flow):
    # First, it should request the user model
    request = flow.send(None)
    assert isinstance(request, urllib.request.Request)
    assert request.get_full_url() == "http://my-hub.com/hub/api/user"
    assert request.get_method() == "GET"

    # We send our 200 response and then a token
    response = NetworkResponse(200, {}, object())
    request = flow.send(response)

    # Ensure it's reading this obj
    assert isinstance(request, Read)
    assert request.readable is response

    # Ensure that we get the proper result!
    request = flow.send(
        json.dumps(
            {"name": "bob", "servers": {"": {"ready": True, "url": "/user/bob"}}}
        ).encode("utf-8")
    )
    assert isinstance(request, urllib.request.Request)
    assert request.get_full_url() == "http://my-hub.com/hub/api/users/bob/server"
    assert request.get_method() == "DELETE"

    # We send our 200 response and then a token
    response = NetworkResponse(202, {}, object())
    request = flow.send(response)

    # Expect sleep request
    assert isinstance(request, Sleep)

    # Respond with sleep result (None)
    request = flow.send(None)

    # Expect flow to check status
    assert isinstance(request, urllib.request.Request)
    assert request.get_full_url() == "http://my-hub.com/hub/api/user"
    assert request.get_method() == "GET"

    # We send our 200 response and then a token
    response = NetworkResponse(200, {}, object())
    request = flow.send(response)

    # Ensure it's reading this obj
    assert isinstance(request, Read)
    assert request.readable is response

    with pytest.raises(StopIteration):
        flow.send(json.dumps({"name": "bob", "servers": {}}).encode("utf-8"))
