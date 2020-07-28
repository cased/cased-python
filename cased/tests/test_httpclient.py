import pytest
import cased
from cased.tests.util import mock_requests
from cased.http import HTTPClient

import requests

import responses
from responses import GET, POST, PATCH, PUT, DELETE, HEAD


class TestHTTPClient(object):
    @responses.activate
    def test_http_client_get(self):
        mock_requests("/data", method=GET)

        cased.api_key = "cs_test_001"
        assert (
            HTTPClient.make_request(
                "get", cased.api_base + "/data", cased.api_key
            ).status_code
            == 200
        )

    @responses.activate
    def test_http_client_post(self):
        mock_requests("/publish", method=POST)
        cased.api_key = "cs_test_001"

        assert (
            HTTPClient.make_request(
                "post", cased.api_base + "/publish", "data"
            ).status_code
            == 200
        )

    @responses.activate
    def test_http_client_put(self):
        mock_requests("/data", method=PUT)
        cased.api_key = "cs_test_001"

        assert (
            HTTPClient.make_request("put", cased.api_base + "/data", "data").status_code
            == 200
        )

    @responses.activate
    def test_http_client_patch(self):
        mock_requests("/data", method=PATCH)
        cased.api_key = "cs_test_001"

        assert (
            HTTPClient.make_request(
                "patch", cased.api_base + "/data", "data"
            ).status_code
            == 200
        )

    @responses.activate
    def test_http_client_head(self):
        mock_requests("/data", method=HEAD)
        cased.api_key = "cs_test_001"

        assert (
            HTTPClient.make_request(
                "head", cased.api_base + "/data", cased.api_key
            ).status_code
            == 200
        )

    @responses.activate
    def test_http_client_delete(self):
        mock_requests("/data", method=DELETE)
        cased.api_key = "cs_test_001"

        assert (
            HTTPClient.make_request(
                "delete", cased.api_base + "/data", cased.api_key
            ).status_code
            == 200
        )
