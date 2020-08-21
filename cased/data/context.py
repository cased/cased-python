from threading import local

cased_threadlocals = local()


class Context:
    @classmethod
    def current(cls):
        return cls._data()

    @classmethod
    def clear(cls):
        setattr(cased_threadlocals, "cased_context", {})

    @classmethod
    def update(cls, data):
        latest_data = cls._data()
        latest_data.update(data)
        cls._set_data(latest_data)
        return cls._data()

    @classmethod
    def _data(cls):
        return getattr(cased_threadlocals, "cased_context", {})

    @classmethod
    def _set_data(cls, data):
        setattr(cased_threadlocals, "cased_context", data)
        return cls._data()
