import re

import cased
from cased.data.sensitive import SensitiveDataHandler, SensitiveDataProcessor

username_regex = r"@([A-Za-z0-9_]+)"
name_regex = r"Smith"


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

event_with_multiple_keys_of_different_matches = {
    "actor": "some-actor",
    "action": "user.create",
    "name": "Jane Smith",
    "new_username": "@someusername",
    "phone": "555-555-5555",
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
    def teardown_method(self, method):
        cased.Context.clear()
        cased.redact_before_publishing = False

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

    def test_sensitive_data_processor_can_be_created_with_mutiple_handlers(self):
        handler1 = SensitiveDataHandler("username", username_regex)
        handler2 = SensitiveDataHandler("name", name_regex)

        processor = SensitiveDataProcessor(event, [handler1, handler2])
        assert processor.audit_event == event
        assert processor.data_handlers == [handler1, handler2]

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

    def test_ranges_from_event_works_with_multiple_handlers(self):
        handler1 = SensitiveDataHandler("username", username_regex)
        handler2 = SensitiveDataHandler("name", name_regex)

        processor = SensitiveDataProcessor(
            event_with_multiple_keys_of_different_matches.copy(), [handler1, handler2]
        )

        assert processor.process()[".cased"]["pii"] == {
            "new_username": [{"begin": 0, "end": 13, "label": "username"}],
            "name": [{"begin": 5, "end": 10, "label": "name"}],
        }

    def test_ranges_from_event_works_with_multiple_handlers_and_field_setting(self):
        handler1 = SensitiveDataHandler("username", username_regex)
        handler2 = SensitiveDataHandler("name", name_regex)
        cased.add_sensitive_field("phone")

        processor = SensitiveDataProcessor(
            event_with_multiple_keys_of_different_matches.copy(), [handler1, handler2]
        )

        assert processor.process()[".cased"]["pii"] == {
            "new_username": [{"begin": 0, "end": 13, "label": "username"}],
            "name": [{"begin": 5, "end": 10, "label": "name"}],
            "phone": [{"begin": 0, "end": 12, "label": "phone"}],
        }

        cased.sensitive_fields = set()

    def test_ranges_from_event_works_with_multiple_key_matches(self):
        handler = SensitiveDataHandler("username", username_regex)
        processor = SensitiveDataProcessor(
            event_with_multiple_keys_matching.copy(), [handler]
        )

        assert processor.ranges_from_event(
            event_with_multiple_keys_matching.copy(), handler
        ) == {
            "friend_username": [{"begin": 0, "end": 15, "label": "username"}],
            "new_username": [
                {"begin": 0, "end": 13, "label": "username"},
                {"begin": 23, "end": 39, "label": "username"},
            ],
        }

    def test_add_ranges_to_events(self):
        handler = SensitiveDataHandler("username", username_regex)
        processor = SensitiveDataProcessor(event.copy(), [handler])
        ranges = {"new_username": [{"begin": 0, "end": 13, "label": "username"}]}

        assert processor.add_ranges_to_event(ranges) == {
            ".cased": {
                "pii": {
                    "new_username": [{"begin": 0, "end": 13, "label": "username"}],
                },
            },
            "action": "user.create",
            "actor": "some-actor",
            "new_username": "@someusername",
        }

    def test_add_ranges_to_event_with_multiple_key_matches(self):
        handler = SensitiveDataHandler("username", username_regex)
        processor = SensitiveDataProcessor(
            event_with_multiple_keys_matching.copy(), [handler]
        )
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

    def test_redact_data(self):
        handler = SensitiveDataHandler("username", username_regex)
        processor = SensitiveDataProcessor(
            event_with_multiple_keys_matching.copy(), [handler]
        )

        ranges = {
            "friend_username": [{"begin": 0, "end": 15, "label": "username"}],
            "new_username": [
                {"begin": 0, "end": 13, "label": "username"},
                {"begin": 23, "end": 39, "label": "username"},
            ],
        }

        assert processor.redact_data(ranges) == {
            "action": "user.create",
            "actor": "some-actor",
            "friend_username": "XXXXXXXXXXXXXXX",
            "new_username": "XXXXXXXXXXXXX and also XXXXXXXXXXXXXXXX",
        }

    def test_redact_data_with_multiple_key_matches(self):
        handler = SensitiveDataHandler("username", username_regex)
        processor = SensitiveDataProcessor(
            event_with_multiple_keys_matching.copy(), [handler]
        )

        ranges = {
            "friend_username": [{"begin": 0, "end": 15, "label": "username"}],
            "new_username": [
                {"begin": 0, "end": 13, "label": "username"},
                {"begin": 23, "end": 39, "label": "username"},
            ],
        }

        assert processor.redact_data(ranges) == {
            "action": "user.create",
            "actor": "some-actor",
            "friend_username": "XXXXXXXXXXXXXXX",
            "new_username": "XXXXXXXXXXXXX and also XXXXXXXXXXXXXXXX",
        }

    def test_redact_data_with_multiple_handlers(self):
        cased.redact_before_publishing = True

        handler1 = SensitiveDataHandler("username", username_regex)
        handler2 = SensitiveDataHandler("name", name_regex)

        processor = SensitiveDataProcessor(
            event_with_multiple_keys_of_different_matches.copy(), [handler1, handler2]
        )

        assert processor.process() == {
            ".cased": {
                "pii": {
                    "new_username": [{"begin": 0, "end": 13, "label": "username"}],
                    "name": [{"begin": 5, "end": 10, "label": "name"}],
                }
            },
            "name": "Jane XXXXX",
            "action": "user.create",
            "actor": "some-actor",
            "phone": "555-555-5555",
            "new_username": "XXXXXXXXXXXXX",
        }

    def test_process_does_everything_needed(self):
        handler = SensitiveDataHandler("username", username_regex)
        processor = SensitiveDataProcessor(
            event_with_multiple_keys_matching.copy(), [handler]
        )
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

    def test_process_does_everything_needed_with_redact_configured(self):
        cased.redact_before_publishing = True
        handler = SensitiveDataHandler("username", username_regex)
        processor = SensitiveDataProcessor(
            event_with_multiple_keys_matching.copy(), [handler]
        )
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
            "friend_username": "XXXXXXXXXXXXXXX",
            "new_username": "XXXXXXXXXXXXX and also XXXXXXXXXXXXXXXX",
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
