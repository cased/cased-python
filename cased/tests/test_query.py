import pytest

import cased
from cased.data.query import Query


class TestQuery:
    def test_basic_query_make_phrase(self):
        data = {"event": "user.login"}
        phrase = Query.make_phrase_from_dict(data)

        assert phrase == "(event:user.login)"

    def test_make_phrase_with_empty_dict(self):
        data = {}
        phrase = Query.make_phrase_from_dict(data)

        assert phrase == "()"

    def test_make_phrase_with_multiple_keys(self):
        data = {"event": "user.login", "actor": "test-user"}
        phrase = Query.make_phrase_from_dict(data)

        assert phrase == "(event:user.login AND actor:test-user)"
