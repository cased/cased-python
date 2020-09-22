try:
    from unittest import mock
except ImportError:
    import mock

import cased
from cased.data.reliability import AbstractReliabilityBackend
import requests
import responses


class SimpleReliabilityBackend(AbstractReliabilityBackend):
    def __init__(self):
        self.data_store = []

    def add(self, data):
        self.data_store.append(data)
        return True


class MockPublisher(object):
    def __init__(self):
        pass

    def publish(self, data):
        return {}


class EmptyClass:
    def __init__(self):
        pass


# HTTP Response Mock
def mock_response(
    status_code=200, content="response content", headers={}, json_data=None, **params
):
    mock_res = mock.Mock()
    mock_res.status_code = status_code
    mock_res.content = content
    mock_res.headers = headers

    if json_data:
        mock_res.json = mock.Mock(return_value=json_data)

    return mock.patch.object(
        cased.http.HTTPClient, "make_request", return_value=mock_res
    )


def mock_requests(
    path, response={}, content_type="application/json", status=200, method=responses.GET
):
    """
    Mock the requests library.

    ONLY use this for testing the low-level HTTPClient itself — it should not be used
    for testing any Cased API routes. Instead use mock_response().
    """
    url = cased.api_base + path
    responses.add(method, url, json=response, status=status, content_type=content_type)


def mock_redis_backend_add():
    return mock.patch.object(
        cased.data.reliability.RedisReliabilityBackend, "add", return_value=1
    )
