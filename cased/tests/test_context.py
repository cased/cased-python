from unittest.mock import ANY
import pytest

import threading

import cased

from cased.data.context import Context


class TestContext(object):
    def teardown_method(self, method):
        # Clear the context after each test
        Context.clear()

    def test_context_current_returns_empty_dict(self):
        assert Context.current() == {}

    def test_context_can_be_updated(self):
        Context.update({"username": "test"})
        assert Context.current() == {"username": "test"}

    def test_context_can_be_cleared(self):
        Context.update({"username": "test"})
        assert Context.current() == {"username": "test"}
        Context.clear()
        assert Context.current() == {}

    def test_context_can_be_cleared_and_then_updated(self):
        Context.update({"username": "test"})
        assert Context.current() == {"username": "test"}
        Context.clear()
        assert Context.current() == {}
        Context.update({"username": "test"})
        assert Context.current() == {"username": "test"}

    def test_context_can_be_updated_twice(self):
        Context.update({"username": "test"})
        assert Context.current() == {"username": "test"}
        Context.update({"username": "foo"})
        assert Context.current() == {"username": "foo"}

    def test_context_can_be_updated_and_another_field_updated(self):
        Context.update({"username": "test"})
        assert Context.current() == {"username": "test"}
        Context.update({"action": "test.action"})
        assert Context.current() == {"username": "test", "action": "test.action"}

    def test_context_can_be_accessed_globally(self):
        assert cased.Context == Context

    def test_context_can_be_updated_globally(self):
        cased.Context.update({"username": "test"})
        assert Context.current() == {"username": "test"}

    def test_context_can_be_updated_twice_globally(self):
        cased.Context.update({"username": "test"})
        assert Context.current() == {"username": "test"}
        cased.Context.update({"username": "foo"})
        assert Context.current() == {"username": "foo"}

    def test_context_can_be_updated_and_another_field_updated_globally(self):
        cased.Context.update({"username": "test"})
        assert Context.current() == {"username": "test"}
        cased.Context.update({"action": "test.action"})
        assert Context.current() == {"username": "test", "action": "test.action"}

    def test_context_can_be_read_globally(self):
        cased.Context.update({"username": "test"})
        assert cased.Context.current() == {"username": "test"}

    def test_context_is_per_thread(self):
        t1_output = {}
        t2_output = {}
        t3_output = {}

        def write_to_output(data, target):
            cased.Context.update(data)
            target.update(cased.Context.current())

        t1 = threading.Thread(
            target=write_to_output, args=({"action": "test.one"}, t1_output)
        )
        t2 = threading.Thread(
            target=write_to_output, args=({"action": "test.two"}, t2_output)
        )
        t3 = threading.Thread(
            target=write_to_output,
            args=({"action": "test.three", "user": "test-user"}, t3_output),
        )

        t1.start()
        t2.start()
        t3.start()

        assert t1_output == {"action": "test.one"}
        assert t2_output == {"action": "test.two"}
        assert t3_output == {"action": "test.three", "user": "test-user"}

