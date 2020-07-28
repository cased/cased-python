import uuid
from datetime import datetime, timezone


class DataPlugin:
    """
    Base class for implementing DataPlugins.

    To use, subclass this class and implement additions(), which returns a dict.
    """

    def __init__(self, data):
        copied_data = data.copy()
        self.data = copied_data

    def additions(self):
        raise NotImplementedError("Implement additions() in subclasses of DataPlugin")


class CasedDefaultPlugin(DataPlugin):
    """
    Default plugin that adds a random cased_id and a timestamp to every audit entry
    """

    def additions(self):
        return {
            "cased_id": uuid.uuid4().hex,
            "timestamp": str(
                datetime.now(timezone.utc).isoformat(timespec="microseconds")
            ),
        }
