from unittest.mock import ANY
import pytest

import cased

from cased.tests.util import mock_response
from cased.api.policy import Policy


class TestPolicy(object):
    def test_policy_can_fetch(self):
        with mock_response():
            cased.api_key = "cs_test_001"

            assert Policy.fetch("1234").status_code == 200

    def test_policy_fetch_request_is_called_with_an_event_id(self):
        with mock_response():
            cased.api_key = "cs_test_001"

            assert Policy.fetch("1234")

            cased.http.HTTPClient.make_request.assert_called_with(
                "get", "https://api.cased.com/policies/1234", "cs_test_001", None
            )

    def test_policies_are_listable(self):
        with mock_response():
            cased.api_key = "cs_test_001"

            assert Policy.list().json_response

    def test_policy_list_request_can_set_page_limit(self):
        with mock_response():
            cased.api_key = "cs_test_001"

            Policy.list(limit=10)

            cased.http.HTTPClient.make_request.assert_called_with(
                "get",
                "https://api.cased.com/policies/",
                "cs_test_001",
                {"per_page": 10},
            )

    def test_policy_list_request_is_called_with_correct_url(self):
        with mock_response():
            cased.api_key = "cs_test_001"

            Policy.list()

            cased.http.HTTPClient.make_request.assert_called_with(
                "get",
                "https://api.cased.com/policies/",
                "cs_test_001",
                {"per_page": 25},
            )

    def test_policy_can_create(self):
        with mock_response():
            cased.api_key = "cs_test_001"

            assert (
                Policy.create(
                    name="my-policy", description="policy description"
                ).status_code
                == 200
            )

    def test_policy_create_request_has_correct_paramaters(self):
        with mock_response():
            cased.api_key = "cs_test_001"

            Policy.create(name="my-policy", description="policy description")

            cased.http.HTTPClient.make_request.assert_called_with(
                "post",
                "https://api.cased.com/policies/",
                "cs_test_001",
                {"name": "my-policy", "description": "policy description"},
            )

    def test_policy_can_delete(self):
        with mock_response(status_code=204):
            cased.api_key = "cs_test_001"

            assert Policy.delete("12345").status_code == 204

    def test_policy_delete_request_has_correct_paramaters(self):
        with mock_response(status_code=204):
            cased.api_key = "cs_test_001"

            assert Policy.delete("12345").status_code == 204

            cased.http.HTTPClient.make_request.assert_called_with(
                "delete", "https://api.cased.com/policies/12345", "cs_test_001", None
            )
