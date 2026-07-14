from hucl.flows.user_delete import delete_user_sansio
from hucl.drivers.sansio import NetworkResponse
import urllib.request
import pytest


@pytest.fixture
def flow():
    return delete_user_sansio(
        api_url="http://my-hub.com/hub/api", api_token="123456-a-token", user_name="bob"
    )


def test_user_doesnt_exists(flow):
    # First, it should request the user model
    request = flow.send(None)
    assert isinstance(request, urllib.request.Request)
    assert request.get_full_url() == "http://my-hub.com/hub/api/users/bob"
    assert request.get_method() == "DELETE"

    # We send our 200 response and then a token
    response = NetworkResponse(404, {}, object())
    with pytest.raises(StopIteration):
        flow.send(response)


def test_user_was_deleted(flow):
    # First, it should request the user model
    request = flow.send(None)
    assert isinstance(request, urllib.request.Request)
    assert request.get_full_url() == "http://my-hub.com/hub/api/users/bob"
    assert request.get_method() == "DELETE"

    # We send our 200 response and then a token
    response = NetworkResponse(204, {}, object())
    with pytest.raises(StopIteration):
        flow.send(response)


def test_user_error_unknown(flow):
    # First, it should request the user model
    request = flow.send(None)
    assert isinstance(request, urllib.request.Request)
    assert request.get_full_url() == "http://my-hub.com/hub/api/users/bob"
    assert request.get_method() == "DELETE"

    # We send our 200 response and then a token
    response = NetworkResponse(500, {}, object())
    with pytest.raises(RuntimeError, match=r"Expected HTTP 204"):
        flow.send(response)
