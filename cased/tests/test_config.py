import os
import importlib
import sys
import pytest
import cased


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
