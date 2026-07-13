from jupyterhub_client.flows.spawn import start_server_sansio
from jupyterhub_client.drivers.sansio import Read, ReadLine, NetworkResponse, Sleep
import urllib.request
import json
import pytest


def test_unnamed_already_exists():
    flow = start_server_sansio("http://my-hub.com/hub/api", "123456-a-token", None, {})

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
    with pytest.raises(StopIteration, match=r"/user/bob"):
        request = flow.send(
            json.dumps(
                {"name": "bob", "servers": {"": {"ready": True, "url": "/user/bob"}}}
            ).encode("utf-8")
        )


def test_unnamed_doesnt_exist_is_created():
    flow = start_server_sansio("http://my-hub.com/hub/api", "123456-a-token", None, {})

    # First, Flow should request the user model
    request = flow.send(None)
    assert isinstance(request, urllib.request.Request)
    assert request.get_method() == "GET"
    assert request.get_full_url() == "http://my-hub.com/hub/api/user"

    # We send our 200 response and then a token
    response = NetworkResponse(200, {}, object())
    request = flow.send(response)

    # Ensure Flow's reading this obj
    assert isinstance(request, Read)
    assert request.readable is response

    # Ensure that we get the proper result!
    request = flow.send(json.dumps({"name": "bob", "servers": {}}).encode("utf-8"))
    assert isinstance(request, urllib.request.Request)
    assert request.get_method() == "POST"
    assert request.get_full_url() == "http://my-hub.com/hub/api/users/bob/server"

    ######### Option 1: HTTP 201 #############
    # Send HTTP 201 Created response
    request = flow.send(NetworkResponse(201, {}, object()))

    # Flow again should check the status
    assert isinstance(request, urllib.request.Request)
    assert request.get_method() == "GET"
    assert request.get_full_url() == "http://my-hub.com/hub/api/user"

    # We send our 200 response and then a token
    response = NetworkResponse(200, {}, response)
    request = flow.send(response)

    # Ensure Flow's reading this obj
    assert isinstance(request, Read)
    assert request.readable is response

    # Ensure that we get the proper result!
    with pytest.raises(StopIteration, match=r"/user/bob/"):
        request = flow.send(
            json.dumps(
                {"name": "bob", "servers": {"": {"ready": True, "url": "/user/bob/"}}}
            ).encode("utf-8")
        )


def test_unnamed_doesnt_exist_is_accepted():
    flow = start_server_sansio("http://my-hub.com/hub/api", "123456-a-token", None, {})

    # First, Flow should request the user model
    request = flow.send(None)
    assert isinstance(request, urllib.request.Request)
    assert request.get_method() == "GET"
    assert request.get_full_url() == "http://my-hub.com/hub/api/user"

    # We send our 200 response and then a token
    response = NetworkResponse(200, {}, object())
    request = flow.send(response)

    # Ensure Flow's reading this obj
    assert isinstance(request, Read)
    assert request.readable is response

    # Ensure that we get the proper result!
    request = flow.send(json.dumps({"name": "bob", "servers": {}}).encode("utf-8"))
    assert isinstance(request, urllib.request.Request)
    assert request.get_method() == "POST"
    assert request.get_full_url() == "http://my-hub.com/hub/api/users/bob/server"

    ######### Option 2: HTTP 202 #############
    # Send HTTP 202 Accepted response
    request = flow.send(NetworkResponse(202, {}, object()))

    # Flow again should check the status
    assert isinstance(request, urllib.request.Request)
    assert request.get_method() == "GET"
    assert (
        request.get_full_url() == "http://my-hub.com/hub/api/users/bob/server/progress"
    )

    # We send our 200 response and then a token
    response = NetworkResponse(200, {}, response)
    request = flow.send(response)

    # Ensure Flow's reading this progress
    assert isinstance(request, ReadLine)
    assert request.readable is response

    request = flow.send(b"some random data")
    assert isinstance(request, ReadLine)
    assert request.readable is response

    request = flow.send(b"some other data")
    assert isinstance(request, ReadLine)
    assert request.readable is response

    request = flow.send(b'data: {"url": "http://some-url"}')
    assert isinstance(request, ReadLine)
    assert request.readable is response

    request = flow.send(b'data: {"ready": false, "url": "/user/bob/"}')
    assert isinstance(request, ReadLine)
    assert request.readable is response

    # Ensure that we get the proper result!
    with pytest.raises(StopIteration, match=r"/user/bob/"):
        flow.send(b'data: {"ready": true, "url": "/user/bob/"}')


def test_unnamed_doesnt_exist_needs_retry():
    flow = start_server_sansio("http://my-hub.com/hub/api", "123456-a-token", None, {})

    # First, Flow should request the user model
    request = flow.send(None)
    assert isinstance(request, urllib.request.Request)
    assert request.get_method() == "GET"
    assert request.get_full_url() == "http://my-hub.com/hub/api/user"

    # We send our 200 response and then a token
    response = NetworkResponse(200, {}, object())
    request = flow.send(response)

    # Ensure Flow's reading this obj
    assert isinstance(request, Read)
    assert request.readable is response

    # Ensure that we get the proper result!
    request = flow.send(json.dumps({"name": "bob", "servers": {}}).encode("utf-8"))
    assert isinstance(request, urllib.request.Request)
    assert request.get_method() == "POST"
    assert request.get_full_url() == "http://my-hub.com/hub/api/users/bob/server"

    ######### Option 3: HTTP 429 #############
    # Send 429 Too Many Requests response
    request = flow.send(NetworkResponse(429, {"Retry-After": "5"}, object()))

    # Flow again should check the status
    assert isinstance(request, Sleep)
    assert request.duration_s == 5

    # We continue
    request = flow.send(None)

    # Flow asks us to create again
    assert isinstance(request, urllib.request.Request)
    assert request.get_method() == "POST"
    assert request.get_full_url() == "http://my-hub.com/hub/api/users/bob/server"


def test_unnamed_exists_stopping():
    flow = start_server_sansio("http://my-hub.com/hub/api", "123456-a-token", None, {})

    # First, Flow should request the user model
    request = flow.send(None)
    assert isinstance(request, urllib.request.Request)
    assert request.get_method() == "GET"
    assert request.get_full_url() == "http://my-hub.com/hub/api/user"

    # We send our 200 response and then a token
    response = NetworkResponse(200, {}, object())
    request = flow.send(response)

    # Ensure Flow's reading this obj
    assert isinstance(request, Read)
    assert request.readable is response

    # Ensure that we get the proper result!
    request = flow.send(
        json.dumps(
            {
                "name": "bob",
                "servers": {
                    "": {
                        "ready": False,
                        "stopped": False,
                        "pending": "stop",
                        "url": "/user/bob/",
                    }
                },
            }
        ).encode("utf-8")
    )

    # Flow will wait and check status
    assert isinstance(request, Sleep)

    # We continue
    request = flow.send(None)

    # Flow will check the status again
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
    with pytest.raises(StopIteration, match=r"/user/bob"):
        request = flow.send(
            json.dumps(
                {"name": "bob", "servers": {"": {"ready": True, "url": "/user/bob"}}}
            ).encode("utf-8")
        )
