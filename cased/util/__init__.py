import logging
import sys
import cased

logger = logging.getLogger("cased")


def log_debug(message):
    if cased.log_level == "debug":
        print(message, file=sys.stderr)
    logger.debug(message)


def log_info(message):
    if cased.log_level in ["debug", "info"]:
        print(message, file=sys.stderr)
    logger.info(message)


def log_error(message):
    if cased.log_level in ["debug", "info", "error"]:
        print(message, file=sys.stderr)
    logger.error(message)


def traverse(data):
    """
    Recursively traverse a nested dictionary (with potential nested values of dict, list, string;
    'final' values are all strings). This function can deal with nested dicts, lists of lists,
    lists of dicts, dicts of lists of lists, etc.

    Returns a dict of flattened key/value pairs.

    In cases where the value is a list of the strings, a list of those strings returned as the value.
    """
    flattened = {}

    def _walk(data):
        """
        Walk a nested dictionary, and write the final key-value pairs to
        the `flattened` list.
        """
        for key, value in data.items():
            if isinstance(value, str):
                # We've hit a string, so set the key/value pair.
                flattened[key] = value
            elif isinstance(value, list):
                # The value is a list, so we need to iterate through it. If the list
                # includes other lists, we'll need to iterate through those too.
                _traverse_list(key, value)
            elif isinstance(value, dict):
                # The value is a dictionary, so recurse.
                _walk(value)

    def _traverse_list(key, items):
        """
        Traverse a list of strings, dicts, or lists, until the final string key-value
        pair is found. Write that pair to the `flattened` list
        """
        for item in items:
            if isinstance(item, str):
                if key in flattened:
                    # The key exists, so append this string to the existing list:
                    #   e.g., {"some_key": ["value1", "value2"]}
                    flattened[key].append(item)
                else:
                    # The key associated with this string does not yet exist in our new
                    # data dictionary. So create a new list of strings and associate it
                    # with that key.
                    flattened[key] = [item]
            elif isinstance(item, list):
                # The item is a list (i.e., a list of a list).
                _traverse_list(key, item)
            else:
                # The item is not a list and not a string (so it's a dict); so walk it.
                _walk(item)

    _walk(data)

    return flattened
