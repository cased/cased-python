from unittest.mock import ANY
import pytest

import cased

from cased.data.reliability import ReliabilityEngineError
from cased.tests.util import mock_response, SimpleReliabilityBackend
from cased.api.event import Event
from cased.data.query import Query
from cased.http import Requestor


class TestEvent(object):
    def teardown_method(self, method):
        cased.Context.clear()
        cased.clear_context_after_publishing = False

    def test_event_can_fetch(self):
        with mock_response():
            cased.policy_key = "cs_test_001"

            assert Event.fetch("1234").status_code == 200

    def test_event_fetch_request_is_called_with_an_event_id(self):
        with mock_response():
            cased.policy_key = "cs_test_001"

            assert Event.fetch("1234")

            cased.http.HTTPClient.make_request.assert_called_with(
                "get", "https://api.cased.com/events/1234", "cs_test_001", None
            )

    def test_events_are_listable(self):
        with mock_response():
            cased.policy_key = "cs_test_001"

            assert Event.list().json_response

    def test_event_list_request_is_called_with_correct_url(self):
        with mock_response():
            cased.policy_key = "cs_test_001"

            Event.list()

            cased.http.HTTPClient.make_request.assert_called_with(
                "get", "https://api.cased.com/events/", "cs_test_001", {"per_page": 25}
            )

    def test_event_list_request_can_set_page_limit(self):
        with mock_response():
            cased.policy_key = "cs_test_001"

            Event.list(limit=10)

            cased.http.HTTPClient.make_request.assert_called_with(
                "get", "https://api.cased.com/events/", "cs_test_001", {"per_page": 10}
            )

    def test_events_can_be_listed_and_filtered_with_variables(self):
        with mock_response():
            cased.policy_key = "cs_test_001"

            Event.list(variables={"team": "team_1"})

            cased.http.HTTPClient.make_request.assert_called_with(
                "get",
                "https://api.cased.com/events/",
                "cs_test_001",
                {"per_page": 25, "variables[team]": "team_1"},
            )

    def test_events_can_be_listed_and_filtered_with_variables_and_works_with_limits(
        self,
    ):
        with mock_response():
            cased.policy_key = "cs_test_001"

            Event.list(limit=10, variables={"team": "team_1"})

            cased.http.HTTPClient.make_request.assert_called_with(
                "get",
                "https://api.cased.com/events/",
                "cs_test_001",
                {"per_page": 10, "variables[team]": "team_1"},
            )

    def test_events_can_be_filtered_with_multiple_variables(self):
        with mock_response():
            cased.policy_key = "cs_test_001"

            Event.list(limit=10, variables={"team": "team_1", "organization": "org_1"})

            cased.http.HTTPClient.make_request.assert_called_with(
                "get",
                "https://api.cased.com/events/",
                "cs_test_001",
                {
                    "per_page": 10,
                    "variables[team]": "team_1",
                    "variables[organization]": "org_1",
                },
            )

    def test_events_filter_variables_requires_a_dict(self):
        with mock_response():
            cased.policy_key = "cs_test_001"

            with pytest.raises(TypeError):
                Event.list(limit=10, variables=["data", "more-data"])

    def test_event_can_publish(self):
        with mock_response():
            cased.publish_key = "cs_test_001"

            assert Event.publish({"user": "test"}).status_code == 200

    def test_event_can_publish_with_reliability_engine_configured(self):
        with mock_response():
            cased.publish_key = "cs_test_001"
            cased.reliability_backend = SimpleReliabilityBackend

            assert Event.publish({"user": "test"}).status_code == 200

    def test_event_can_publish_with_reliability_engine_configured_per_request(self):
        with mock_response():
            cased.publish_key = "cs_test_001"
            cased.reliability_backend = None

            assert (
                Event.publish(
                    {"user": "test"}, backend=SimpleReliabilityBackend
                ).status_code
                == 200
            )

    def test_event_can_still_publish_with_reliability_engine_misconfigured_per_request(
        self,
    ):
        with mock_response():
            cased.publish_key = "cs_test_001"
            cased.reliability_backend = None

            assert Event.publish({"user": "test"}, backend="nothere").status_code == 200

    def test_event_is_extended_with_cased_id_and_timestamp(self):
        with mock_response():
            cased.publish_key = "cs_test_001"

            Event.publish({"user": "test"})

            # Confirm that "cased_id" and "timestamp" have been added to the request
            cased.http.HTTPClient.make_request.assert_called_with(
                "post",
                ANY,
                "cs_test_001",
                {"user": "test", "cased_id": ANY, "timestamp": ANY},
            )

    def test_event_is_updated_with_context(self):
        with mock_response():
            cased.publish_key = "cs_test_001"

            cased.Context.update({"country": "Austria"})

            Event.publish({"user": "test"})

            cased.http.HTTPClient.make_request.assert_called_with(
                "post",
                ANY,
                "cs_test_001",
                {
                    "user": "test",
                    "country": "Austria",
                    "cased_id": ANY,
                    "timestamp": ANY,
                },
            )

    def test_event_local_publish_data_takes_precedence_over_context(self):
        with mock_response():
            cased.publish_key = "cs_test_001"

            cased.Context.update({"country": "Austria", "user": "context-test-user"})

            Event.publish({"user": "test"})

            cased.http.HTTPClient.make_request.assert_called_with(
                "post",
                ANY,
                "cs_test_001",
                {
                    "user": "test",
                    "country": "Austria",
                    "cased_id": ANY,
                    "timestamp": ANY,
                },
            )

    def test_event_local_publish_data_handles_nested_list_updates_gracefully(self):
        with mock_response():
            cased.publish_key = "cs_test_001"

            cased.Context.update(
                {"country": "Austria", "users": ["user-one", "user-two"]}
            )

            Event.publish({"users": ["user-three"]})

            cased.http.HTTPClient.make_request.assert_called_with(
                "post",
                ANY,
                "cs_test_001",
                {
                    "users": ["user-one", "user-two", "user-three"],
                    "country": "Austria",
                    "cased_id": ANY,
                    "timestamp": ANY,
                },
            )

    def test_event_local_publish_data_handles_nested_dict_updates_gracefully(self):
        with mock_response():
            cased.publish_key = "cs_test_001"

            cased.Context.update(
                {
                    "country": "Austria",
                    "mappings": {"user-one": "123", "user-two": "456"},
                }
            )

            Event.publish({"mappings": {"user-three": "789"}})

            cased.http.HTTPClient.make_request.assert_called_with(
                "post",
                ANY,
                "cs_test_001",
                {
                    "mappings": {
                        "user-one": "123",
                        "user-three": "789",
                        "user-two": "456",
                    },
                    "country": "Austria",
                    "cased_id": ANY,
                    "timestamp": ANY,
                },
            )

    def test_event_is_updated_with_context_and_can_be_cleared(self):
        with mock_response():
            cased.publish_key = "cs_test_001"

            cased.Context.update({"country": "Austria"})
            Event.publish({"user": "test"})

            cased.http.HTTPClient.make_request.assert_called_with(
                "post",
                ANY,
                "cs_test_001",
                {
                    "user": "test",
                    "country": "Austria",
                    "cased_id": ANY,
                    "timestamp": ANY,
                },
            )

            cased.Context.clear()
            Event.publish({"user": "test"})
            cased.http.HTTPClient.make_request.assert_called_with(
                "post",
                ANY,
                "cs_test_001",
                {"user": "test", "cased_id": ANY, "timestamp": ANY},
            )

    def test_event_is_updated_with_context_and_context_cleared_if_set(self):
        with mock_response():
            cased.publish_key = "cs_test_001"
            cased.clear_context_after_publishing = True

            cased.Context.update({"country": "Austria"})
            Event.publish({"user": "test"})

            cased.http.HTTPClient.make_request.assert_called_with(
                "post",
                ANY,
                "cs_test_001",
                {
                    "user": "test",
                    "country": "Austria",
                    "cased_id": ANY,
                    "timestamp": ANY,
                },
            )

            Event.publish({"user": "test"})
            cased.http.HTTPClient.make_request.assert_called_with(
                "post",
                ANY,
                "cs_test_001",
                {"user": "test", "cased_id": ANY, "timestamp": ANY},
            )

    def test_event_publish_uses_publish_base(self):
        with mock_response():
            cased.publish_key = "cs_test_001"

            assert Requestor.publish_requestor().api_base == cased.publish_base

    def test_event_can_be_configured_to_not_publish(self):
        with mock_response():
            cased.publish_key = "cs_test_001"
            cased.disable_publishing = True

            assert Event.publish({"user": "test"}) is None

    def test_event_can_list_by_actor(self):
        with mock_response():
            cased.policy_key = "cs_test_001"

            assert Event.list_by_actor("test").results

    def test_event_can_list_by_action(self):
        with mock_response():
            cased.policy_key = "cs_test_001"

            assert Event.list_by_action("user.login").results

    def test_event_list_request_has_correct_paramaters_with_a_long_phrase(self):
        with mock_response():
            cased.policy_key = "cs_test_001"

            Event.list(
                search=Query.make_phrase_from_dict(
                    {"actor": "test", "event": "user.login"}
                )
            )

            cased.http.HTTPClient.make_request.assert_called_with(
                "get",
                "https://api.cased.com/events/",
                "cs_test_001",
                {"per_page": 25, "phrase": "(actor:test AND event:user.login)"},
            )

    def test_event_list_by_actor_request_has_correct_paramaters(self,):
        with mock_response():
            cased.policy_key = "cs_test_001"

            Event.list_by_actor("test")

            cased.http.HTTPClient.make_request.assert_called_with(
                "get",
                "https://api.cased.com/events/",
                "cs_test_001",
                {"per_page": 25, "phrase": "(actor:test)"},
            )

    def test_event_list_by_action_request_has_correct_paramaters(self,):
        with mock_response():
            cased.policy_key = "cs_test_001"

            Event.list_by_action("test-event")

            cased.http.HTTPClient.make_request.assert_called_with(
                "get",
                "https://api.cased.com/events/",
                "cs_test_001",
                {"per_page": 25, "phrase": "(action:test-event)"},
            )

    def test_event_list_by_action_request_api_key_can_be_overrode(self,):
        with mock_response():
            cased.policy_key = "cs_test_001"

            Event.list_by_action("test-event", api_key="alt_key")

            cased.http.HTTPClient.make_request.assert_called_with(
                "get",
                "https://api.cased.com/events/",
                "alt_key",
                {"per_page": 25, "phrase": "(action:test-event)"},
            )

    def test_event_list_by_actor_request_api_key_can_be_overrode(self,):
        with mock_response():
            cased.policy_key = "cs_test_001"

            Event.list_by_actor("test", api_key="alt_key")

            cased.http.HTTPClient.make_request.assert_called_with(
                "get",
                "https://api.cased.com/events/",
                "alt_key",
                {"per_page": 25, "phrase": "(actor:test)"},
            )
