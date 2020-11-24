import os
import importlib
import sys
import pytest
import cased

from cased.tests.util import MockPublisher


def reload_config():
    """
    Reload config helper for tests where we dynamically change the ENV
    """
    importlib.reload(sys.modules["cased"])


class TestConfig(object):
    def test_publish_key_defaults_to_none(self):
        assert cased.publish_key is None

    def test_publish_key_can_be_set(self):
        cased.publish_key = "publish_test_123"
        assert cased.publish_key == "publish_test_123"

    def test_publish_key_can_be_set_from_env(self):
        os.environ["CASED_PUBLISH_KEY"] = "publish_test_abc"
        assert os.environ.get("CASED_PUBLISH_KEY") == "publish_test_abc"

        reload_config()
        import cased

        assert cased.publish_key == "publish_test_abc"

    def test_publish_key_can_be_set_to_none(self):
        cased.publish_key = None
        assert cased.publish_key is None

    def test_policy_defaults_to_none(self):
        reload_config()
        assert cased.policy_key is None

    def test_policy_key_can_be_set(self):
        cased.policy_key = "policy_test_123"
        assert cased.policy_key == "policy_test_123"

    def test_policy_key_can_be_set_from_env(self):
        os.environ["CASED_POLICY_KEY"] = "policy_test_abc"
        assert os.environ.get("CASED_POLICY_KEY") == "policy_test_abc"

        reload_config()
        import cased

        assert cased.policy_key == "policy_test_abc"

    def test_policy_keys_defaults_to_empty_map(self):
        reload_config()
        assert cased.policy_keys == {}

    def test_policy_keys_can_be_set(self):
        cased.policy_keys = {"default": "policy_test_1", "secondary": "policy_test_2"}
        assert cased.policy_keys == {
            "default": "policy_test_1",
            "secondary": "policy_test_2",
        }

    def test_extra_ua_data_defaults_to_none(self):
        reload_config()
        assert cased.extra_ua_data is None

    def test_extra_ua_data_can_be_set(self):
        reload_config()
        cased.extra_ua_data = "library wrap"
        assert cased.extra_ua_data == "library wrap"

    def test_clear_after_publish_default_to_false(self):
        assert not cased.clear_context_after_publishing

    def test_clear_after_publish_default_can_be_set(self):
        cased.clear_context_after_publishing = True
        assert cased.clear_context_after_publishing

        cased.clear_context_after_publishing = False
        assert not cased.clear_context_after_publishing

    def test_publishers_can_added(self):
        reload_config()
        assert cased.additional_publishers == []
        pub = MockPublisher()
        cased.add_publisher(pub)
        assert cased.additional_publishers == [pub]

    def test_publishers_can_remove(self):
        reload_config()
        assert cased.additional_publishers == []
        pub = MockPublisher()

        cased.add_publisher(pub)
        assert cased.additional_publishers == [pub]
        cased.remove_publisher(pub)
        assert cased.additional_publishers == []
