import pytest
import cased
from cased.tests.util import mock_response
from cased.http import HTTPClient
from cased.plugins import DataPlugin, CasedDefaultPlugin


class SimplePlugin(DataPlugin):
    def additions(self):
        return {"test": "test-data"}


class TestHTTPClient(object):
    def test_plugin_can_be_created(self):
        data = {}
        plugin = SimplePlugin(data)
        assert plugin.additions() == {"test": "test-data"}

    def test_plugin_fails_on_abstract_class(self):
        data = {}
        plugin = DataPlugin(data)
        with pytest.raises(NotImplementedError):
            plugin.additions()

    def test_plugins_have_default_plugin(self):
        assert cased.data_plugins == [CasedDefaultPlugin]

    def test_plugins_can_be_added(self):
        assert cased.data_plugins == [CasedDefaultPlugin]
        cased.add_plugin(SimplePlugin)
        assert cased.data_plugins == [CasedDefaultPlugin, SimplePlugin]

    def test_plugins_can_be_removed(self):
        cased.data_plugins = [CasedDefaultPlugin]
        cased.remove_plugin(CasedDefaultPlugin)
        assert cased.data_plugins == []
