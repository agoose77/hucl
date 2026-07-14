from hucl.flows.user_create import create_user_sansio
from hucl.sansio import NetworkResponse
import urllib.request
import json
import pytest


@pytest.fixture
def flow():
    return create_user_sansio(
        api_url="http://my-hub.com/hub/api", api_token="123456-a-token", user_name="bob"
    )


@pytest.fixture
def admin_flow():
    return create_user_sansio(
        api_url="http://my-hub.com/hub/api",
        api_token="123456-a-token",
        user_name="bob",
        admin=True,
    )


def test_user_already_exists(flow):
    # First, it should request the user model
    request = flow.send(None)
    assert isinstance(request, urllib.request.Request)
    assert request.get_full_url() == "http://my-hub.com/hub/api/users/bob"
    assert request.get_method() == "POST"

    # We send our 200 response and then a token
    response = NetworkResponse(409, {}, object())
    with pytest.raises(StopIteration):
        flow.send(response)


def test_user_was_created(flow):
    # First, Flow should request the user model
    request = flow.send(None)
    assert isinstance(request, urllib.request.Request)
    assert request.get_method() == "POST"
    assert request.get_full_url() == "http://my-hub.com/hub/api/users/bob"

    # We send our 200 response and then a token
    response = NetworkResponse(201, {}, object())
    with pytest.raises(StopIteration):
        flow.send(response)


def test_admin_user_was_created(admin_flow):
    # First, Flow should request the user model
    request = admin_flow.send(None)
    assert isinstance(request, urllib.request.Request)
    assert request.get_method() == "POST"
    assert request.get_full_url() == "http://my-hub.com/hub/api/users/bob"

    # We send our 200 response and then a token
    response = NetworkResponse(201, {}, object())
    request = admin_flow.send(response)
    assert isinstance(request, urllib.request.Request)
    assert request.get_method() == "PATCH"
    assert json.loads(request.data) == {"admin": True}
    assert request.get_full_url() == "http://my-hub.com/hub/api/users/bob"

    # We send our 200 response and then a token
    response = NetworkResponse(200, {}, object())
    with pytest.raises(StopIteration):
        admin_flow.send(response)
