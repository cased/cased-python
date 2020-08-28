import cased
from cased.util import traverse
import re


class SensitiveDataHandler:
    """
    Represents a piece of sensitive data.
    """

    def __init__(self, label, pattern):
        self.label = label
        self.pattern = pattern

    def find_matches(self, data):
        """
        Given a string `data`, check if the string matches the sensitive data
        pattern, and return a list of regex matcher object.
        """
        matches = re.finditer(self.pattern, data)

        # A list of all matches
        return [m for m in matches]


class SensitiveDataProcessor:
    """
    Given a list of handlers, process an audit event to find sensitive data.
    Uses the global cased handlers, unless given specific handlers.
    """

    def __init__(self, audit_event, handlers=[]):
        if not isinstance(handlers, list):
            raise Exception("Handlers must be a list.")
        self.audit_event = audit_event
        self._handlers = handlers
        self._sensitive_fields = cased.sensitive_fields

    @property
    def data_handlers(self):
        if not self._handlers:
            handlers = cased.sensitive_data_handlers
        else:
            handlers = self._handlers

        return handlers

    @property
    def sensitive_fields(self):
        return self._sensitive_fields

    def process(self):
        ranges = {}
        flat_events = traverse(self.audit_event)

        for handler in self.data_handlers:
            _ranges = self.ranges_from_event(flat_events, handler)
            ranges.update(_ranges)

        for field in self.sensitive_fields:
            for key, value in flat_events.items():
                if key == field:
                    ranges[key] = [{"label": field, "begin": 0, "end": len(value)}]

        if ranges:
            if cased.redact_before_publishing:
                self.redact_data(ranges)

            return self.add_ranges_to_event(ranges)
        else:
            # Nothing added, just return the original event
            return self.audit_event

    def ranges_from_event(self, flat_events, handler):
        """
        Return ranges from a event, grouped by the key.
        """
        ranges = {}
        for key, value in flat_events.items():
            matches = handler.find_matches(value)
            for match in matches:
                if not ranges.get(key):
                    ranges[key] = []

                begin = match.start()
                end = match.end()

                data_range = {"label": handler.label, "begin": begin, "end": end}

                ranges[key].append(data_range)

        return ranges

    def add_ranges_to_event(self, ranges):
        pii = {}
        # `ranges` is a dict. The key is the event payload key;
        # the value is a list of any sensitive data ranges (as hashes)
        # associated with that key
        for k, v in ranges.items():
            pii[k] = v

        audit_event = self.audit_event
        if not audit_event.get(".cased"):
            audit_event[".cased"] = {}

        audit_event[".cased"]["pii"] = pii
        return audit_event

    def redact_data(self, ranges):
        audit_event = self.audit_event

        for k, v in ranges.items():
            # Get the list of sensitive data in this field
            data_list = ranges.get(k)

            for data_range in data_list:
                begin = data_range.get("begin")
                end = data_range.get("end")

                # find the key in the audit_event
                field_value = audit_event.get(k)
                redaction_length = end - begin
                redact_string = "X" * redaction_length
                new_value = redact_string.join([field_value[:begin], field_value[end:]])
                audit_event[k] = new_value

        return audit_event
