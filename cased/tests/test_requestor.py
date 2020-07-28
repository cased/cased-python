import pytest

import cased
from cased import errors
from cased.tests.util import mock_response
from cased.http import Requestor


class TestAPIRequestor(object):
    ## Tests
    def test_requestor_has_publish_api_key(self):
        with mock_response():
            cased.publish_key = "cs_test_001"

            requestor = Requestor.publish_requestor()
            assert requestor.api_key == "cs_test_001"
            assert requestor.request("post", "/publish").status_code == 200

    def test_requestor_has_policy_api_key(self):
        with mock_response():
            cased.policy_key = "cs_test_001"

            requestor = Requestor.policy_requestor()
            assert requestor.api_key == "cs_test_001"
            assert requestor.request("get", "/policies").status_code == 200

    def test_requestor_has_publish_api_key_on_404(self):
        with mock_response(status_code=404):
            cased.policy_key = "cs_test_001"

            requestor = Requestor.publish_requestor()
            assert requestor.api_key == "cs_test_001"
            assert requestor.request("post", "/publish").status_code == 404

    def test_requestor_has_policy_api_key_on_404(self):
        with mock_response(status_code=404):
            cased.policy_key = "cs_test_001"

            requestor = Requestor.policy_requestor()
            assert requestor.api_key == "cs_test_001"
            assert requestor.request("get", "/policies").status_code == 404

    def test_requestor_fails_without_policy_api_key_on_get(self):
        with mock_response():
            cased.policy_key = None

            with pytest.raises(Exception):
                requestor = Requestor.policy_requestor()
                requestor.request("get", "/publish").status_code

    def test_requestor_fails_without_publish_api_key_on_post(self):
        with mock_response():
            cased.publish_key = None

            with pytest.raises(Exception):
                requestor = Requestor.publish_requestor()
                requestor.request("post", "/publish").status_code
