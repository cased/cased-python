import re

import cased
from cased.data.sensitive import SensitiveDataHandler, SensitiveDataProcessor

username_regex = r"@([A-Za-z0-9_]+)"

event = {
    "actor": "some-actor",
    "action": "user.create",
    "new_username": "@someusername",
}

event_with_two_usernames = {
    "actor": "some-actor",
    "action": "user.create",
    "new_username": "@someusername and also @anotherusername",
}

event_with_multiple_keys_matching = {
    "actor": "some-actor",
    "action": "user.create",
    "new_username": "@someusername and also @anotherusername",
    "friend_username": "@friendusername",
}

event_with_email_field = {
    "actor": "some-actor",
    "action": "user.create",
    "email": "example@example.com",
}

event_with_email_and_phone_field = {
    "actor": "some-actor",
    "action": "user.create",
    "email": "example@example.com",
    "phone": "555-555-5555",
}


class TestSensitiveData(object):
    def test_data_handler_can_be_created(self):
        handler = SensitiveDataHandler("username", username_regex)
        assert handler.label == "username"
        assert handler.pattern == username_regex

    def test_data_handler_finds_matches(self):
        handler = SensitiveDataHandler("username", username_regex)
        string = "@someusername"

        match_obj = self._create_match_obj(username_regex, string)

        matches = handler.find_matches(string)
        assert len(matches) == 1
        assert matches[0].span() == match_obj.span()

    def test_data_handler_finds_multiple_matches(self):
        handler = SensitiveDataHandler("username", username_regex)
        string = "@someusername @anotherusername"
        matches = handler.find_matches(string)

        assert len(matches) == 2

    def test_data_handler_finds_mixed_matches(self):
        handler = SensitiveDataHandler("username", username_regex)
        string = "someusername @anotherusername"
        matches = handler.find_matches(string)

        assert len(matches) == 1

    def test_data_handler_finds_no_matches(self):
        handler = SensitiveDataHandler("username", username_regex)
        string = "nada nope"
        matches = handler.find_matches(string)

        assert len(matches) == 0

    def test_data_handler_works_with_empty_string(self):
        handler = SensitiveDataHandler("username", username_regex)
        string = ""
        matches = handler.find_matches(string)

        assert len(matches) == 0

    def test_sensitive_data_processor_can_be_created(self):
        processor = SensitiveDataProcessor(event)
        assert processor.audit_event == event

    def test_sensitive_data_processor_can_be_created_with_a_handler(self):
        handler = SensitiveDataHandler("username", username_regex)
        processor = SensitiveDataProcessor(event, [handler])
        assert processor.audit_event == event
        assert processor.data_handlers == [handler]

    def test_handlers_can_be_added_and_removed_globally(self):
        assert cased.sensitive_data_handlers == []

        handler = SensitiveDataHandler("username", username_regex)
        cased.add_handler(handler)

        assert cased.sensitive_data_handlers == [handler]

        cased.clear_handlers()
        assert cased.sensitive_data_handlers == []

    def test_sensitive_data_processor_has_default_handlers_if_set(self):
        handler = SensitiveDataHandler("username", username_regex)
        cased.add_handler(handler)

        processor = SensitiveDataProcessor(event)
        assert processor.data_handlers[0].label == handler.label

        cased.clear_handlers()

    def test_ranges_from_event(self):
        handler = SensitiveDataHandler("username", username_regex)
        processor = SensitiveDataProcessor(event, [handler])

        assert processor.ranges_from_event(event, handler) == {
            "new_username": [{"begin": 0, "end": 13, "label": "username"}]
        }

    def test_ranges_from_event_works_with_multiple_matches(self):
        handler = SensitiveDataHandler("username", username_regex)
        processor = SensitiveDataProcessor(event_with_two_usernames, [handler])

        assert processor.ranges_from_event(event_with_two_usernames, handler) == {
            "new_username": [
                {"begin": 0, "end": 13, "label": "username"},
                {"begin": 23, "end": 39, "label": "username"},
            ]
        }

    def test_ranges_from_event_works_with_multiple_key_matches(self):
        handler = SensitiveDataHandler("username", username_regex)
        processor = SensitiveDataProcessor(event_with_multiple_keys_matching, [handler])

        assert processor.ranges_from_event(
            event_with_multiple_keys_matching, handler
        ) == {
            "friend_username": [{"begin": 0, "end": 15, "label": "username"}],
            "new_username": [
                {"begin": 0, "end": 13, "label": "username"},
                {"begin": 23, "end": 39, "label": "username"},
            ],
        }

    def test_add_ranges_to_event(self):
        handler = SensitiveDataHandler("username", username_regex)
        processor = SensitiveDataProcessor(event_with_multiple_keys_matching, [handler])
        ranges = {
            "friend_username": [{"begin": 0, "end": 15, "label": "username"}],
            "new_username": [
                {"begin": 0, "end": 13, "label": "username"},
                {"begin": 23, "end": 39, "label": "username"},
            ],
        }

        assert processor.add_ranges_to_event(ranges) == {
            ".cased": {
                "pii": {
                    "friend_username": [{"begin": 0, "end": 15, "label": "username"}],
                    "new_username": [
                        {"begin": 0, "end": 13, "label": "username"},
                        {"begin": 23, "end": 39, "label": "username"},
                    ],
                }
            },
            "action": "user.create",
            "actor": "some-actor",
            "friend_username": "@friendusername",
            "new_username": "@someusername and also @anotherusername",
        }

    def test_process_does_everything_needed(self):
        handler = SensitiveDataHandler("username", username_regex)
        processor = SensitiveDataProcessor(event_with_multiple_keys_matching, [handler])
        assert processor.process() == {
            ".cased": {
                "pii": {
                    "friend_username": [{"begin": 0, "end": 15, "label": "username"}],
                    "new_username": [
                        {"begin": 0, "end": 13, "label": "username"},
                        {"begin": 23, "end": 39, "label": "username"},
                    ],
                }
            },
            "action": "user.create",
            "actor": "some-actor",
            "friend_username": "@friendusername",
            "new_username": "@someusername and also @anotherusername",
        }

    def test_no_fields_are_marked_as_sensitive_by_default(self):
        assert cased.sensitive_fields == set()

    def test_fields_can_be_marked_as_sensitive(self):
        cased.add_sensitive_field("email")
        assert cased.sensitive_fields == {"email"}

    def test_sensitive_fields_can_be_emptied(self):
        cased.add_sensitive_field("email")
        assert cased.sensitive_fields != set()
        cased.clear_sensitive_fields()
        assert cased.sensitive_fields == set()

    def test_sensitive_data_fields_get_marked_when_added(self):
        cased.add_sensitive_field("email")
        processor = SensitiveDataProcessor(event_with_email_field)

        assert processor.process() == {
            ".cased": {"pii": {"email": [{"begin": 0, "end": 19, "label": "email"}]},},
            "action": "user.create",
            "actor": "some-actor",
            "email": "example@example.com",
        }

        assert len(event_with_email_field["email"]) == 19

    def test_sensitive_data_fields_get_marked_with_explicit_setting(self):
        cased.clear_sensitive_fields()
        cased.sensitive_fields = {"email"}
        processor = SensitiveDataProcessor(event_with_email_field)

        assert processor.process() == {
            ".cased": {"pii": {"email": [{"begin": 0, "end": 19, "label": "email"}]},},
            "action": "user.create",
            "actor": "some-actor",
            "email": "example@example.com",
        }

        assert (
            len(event_with_email_field["email"]) == 19
        )  # to confirm a match with the "end" parameter in pii

    def test_multiple_sensitive_data_fields_get_marked_when_added(self):
        cased.add_sensitive_field("email")
        cased.add_sensitive_field("phone")
        processor = SensitiveDataProcessor(event_with_email_and_phone_field)

        assert processor.process() == {
            ".cased": {
                "pii": {
                    "email": [{"begin": 0, "end": 19, "label": "email"}],
                    "phone": [{"begin": 0, "end": 12, "label": "phone"}],
                }
            },
            "action": "user.create",
            "actor": "some-actor",
            "email": "example@example.com",
            "phone": "555-555-5555",
        }

    # Helpers
    def _create_match_obj(self, regex, string):
        return re.match(regex, string)
