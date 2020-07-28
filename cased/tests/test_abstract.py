import pytest
import cased
from cased.tests.util import mock_response
from cased.api.abstract import CasedAPIResource


class TestAPIResource(object):
    def test_fetch_fails_on_abstract_class(self):
        with mock_response():
            cased.policy_key = "cs_test_001"
            with pytest.raises(NotImplementedError):
                CasedAPIResource.fetch("1234").status_code
