from cased.util import traverse


class TestUtil(object):
    def test_traverse_basics(self):
        data = {"some key": "some value"}
        assert traverse(data) == {"some key": "some value"}

    def test_traverse_with_empty_dict(self):
        data = {}
        assert traverse(data) == {}

    def test_traverse_with_multiple_keys(self):
        data = {"some key": "some value", "another key": "another value"}
        assert traverse(data) == {
            "some key": "some value",
            "another key": "another value",
        }

    def test_traverse_with_nested_dicts(self):
        data = {
            "key-0": {"key-1": "value-1", "key-2": "value-2", "key-3": "value-3"},
            "key-4": "value-4",
        }

        assert traverse(data) == {
            "key-1": "value-1",
            "key-2": "value-2",
            "key-3": "value-3",
            "key-4": "value-4",
        }

    def test_traverse_with_nested_dicts_and_list(self):
        data = {
            "key-0": {
                "key-1": "value-1",
                "key-2": "value-2",
                "key-3": ["value-3", "value-4"],
            },
            "key-4": "value-5",
        }

        assert traverse(data) == {
            "key-1": "value-1",
            "key-2": "value-2",
            "key-3": ["value-3", "value-4"],
            "key-4": "value-5",
        }

    def test_traverse_with_nested_list_of_list(self):
        data = {
            "key-0": {
                "key-1": ["value-0", "value-1"],
                "key-2": [["value-2"], ["value-3"], ["value-4"]],
            }
        }

        assert traverse(data) == {
            "key-1": ["value-0", "value-1"],
            "key-2": ["value-2", "value-3", "value-4"],
        }

    def test_traverse_with_nested_list_of_list_of_lists(self):
        data = {
            "key-0": {
                "key-1": ["value-0", "value-1"],
                "key-2": [
                    ["value-2", ["value-3", "value-4"]],
                    ["value-5"],
                    ["value-6"],
                ],
            }
        }

        assert traverse(data) == {
            "key-1": ["value-0", "value-1"],
            "key-2": ["value-2", "value-3", "value-4", "value-5", "value-6"],
        }

    def test_traverse_with_complex_nested(self):
        data = {
            "key-0": {
                "key-1": "value-1",
                "key-2": "value-2",
                "key-3": ["value-3", "value-4"],
            },
            "key-4": "value-5",
            "key-5": {
                "key-6": ["value-6", "value-7"],
                "key-7": {"key-8": "value-8"},
                "key-9": {
                    "key-10": [
                        {"key-11": "value-10", "key-12": "value-11"},
                        {"key-13": "value-12", "key-14": "value-13"},
                    ]
                },
                "key-15": [["value-15"], ["value-16"]],
            },
        }

        assert traverse(data) == {
            "key-1": "value-1",
            "key-2": "value-2",
            "key-3": ["value-3", "value-4"],
            "key-4": "value-5",
            "key-6": ["value-6", "value-7"],
            "key-8": "value-8",
            "key-11": "value-10",
            "key-12": "value-11",
            "key-13": "value-12",
            "key-14": "value-13",
            "key-15": ["value-15", "value-16"],
        }

    def test_traverse_clobbers_existing_key(self):
        # note: This is not desired behavior. the solution will be some sort of "full path"
        # to the keys. This is also related to the how we'll need to represent lists.
        data = {
            "key-0": {
                "key-will-be-clobbered": "we won't see this",
                "key-1": "value-11",
            },
            "key-will-be-clobbered": "we will see this",
        }

        assert traverse(data) == {
            "key-1": "value-11",
            "key-will-be-clobbered": "we will see this",
        }
