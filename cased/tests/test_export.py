from unittest.mock import ANY
import pytest

import cased

from cased.tests.util import mock_response
from cased.api.export import Export


class TestExport(object):
    def test_export_can_fetch(self):
        with mock_response():
            cased.api_key = "cs_test_001"

            assert Export.fetch("1234").status_code == 200

    def test_export_request_is_called_with_an_event_id(self):
        with mock_response():
            cased.api_key = "cs_test_001"

            assert Export.fetch("1234")

            cased.http.HTTPClient.make_request.assert_called_with(
                "get", "https://api.cased.com/exports/1234", "cs_test_001", None
            )

    def test_export_can_create(self):
        with mock_response():
            cased.api_key = "cs_test_001"

            assert Export.create().status_code == 200

    def test_export_create_request_has_correct_paramaters(self):
        with mock_response():
            cased.api_key = "cs_test_001"

            Export.create()

            cased.http.HTTPClient.make_request.assert_called_with(
                "post", "https://api.cased.com/exports/", "cs_test_001", {}
            )

    def test_export_can_be_downloaded(self):
        with mock_response():
            cased.api_key = "cs_test_001"

            assert Export.download("1234").status_code == 200

    def test_export_download_is_called_correctly(self):
        with mock_response():
            cased.api_key = "cs_test_001"

            assert Export.download("1234")

            cased.http.HTTPClient.make_request.assert_called_with(
                "get",
                "https://api.cased.com/exports/1234/download",
                "cs_test_001",
                None,
            )
