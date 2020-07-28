import cased
import redis


class ReliabilityEngineError(Exception):
    pass


# Single interface to delegate to the backends
class ReliabilityEngine:
    def __init__(self, backend=None):
        """
        Return a ReliabilityEngine with a particular backend.

        `backend` can be either an actual backend class (for example, a custom one),
        or, for convenience, a string of the name of a backend (for example, "redis")

        If `backend` is not given, the global config will be checked — whichever backend
        is specified in the global config will be used. If a `backend` is also not configured there,
        then an exception raised.
        """
        if not backend:
            # No backend given, so use the the config backend
            backend = cased.reliability_backend

        if backend is None:
            raise ReliabilityEngineError(
                """No reliability backend is configured and no backend was passed to ReliabiiltyEngine.
                Set cased.reliability_backend = <your backend> in your global config."""
            )

        if isinstance(backend, str):
            # String was given
            self.engine_backend = self._get_backend_from_name(backend)
        elif issubclass(backend, AbstractReliabilityBackend):
            # Class was given
            self.engine_backend = backend()
        else:
            raise ReliabilityEngineError(
                """Reliability backend is incorrectly configured. Set the backend with
                either a string or a class of your custom backend. You gave: {}""".format(
                    backend
                )
            )

    def _get_backend_from_name(self, name):
        if name == "redis":
            return RedisReliabilityBackend()
        # elif name == "database"
        #   return DatabaseReliabilityBackend() // todo
        else:
            raise ReliabilityEngineError("No backend with name: {}".format(name))

    def add(self, data):
        self.engine_backend.add(data)
        return True


class AbstractReliabilityBackend:
    def __init__(self):
        raise NotImplementedError(
            """Cannot instantiate an AbstractReliabilityBackend"""
        )

    def _split_name_and_get_first(self):
        import re

        name = self.__class__.__name__
        words = re.findall("[A-Z][^A-Z]*", name)
        return words[0].lower()

    @property
    def name(self):
        """
        Name for this backend. Automatically generated based on the first word
        of the class name.
        """
        return self._split_name_and_get_first()

    def add(self, data):
        raise NotImplementedError(
            """add() called on abstract AbstractReliabilityBackend.
                This is likely a bug in the Cased library."""
        )


class RedisReliabilityBackend(AbstractReliabilityBackend):
    def __init__(self, queue_key="cased:reliability_queue"):
        # Get the redis config if it was configured, else an empty dict
        self.config = getattr(cased, "redis_backend_config", {})

        # Key can be configured here, use the default, or be set in the global config
        self.queue_key = queue_key

    def _configure_client(self):
        hostname = self.config.get("hostname") or "localhost"
        port = self.config.get("port") or 6379
        db = self.config.get("db") or 0
        queue_key = self.config.get("queue_key") or self.queue_key

        return hostname, port, db, queue_key

    def _client(self):
        hostname, port, db, queue_key = self._configure_client()
        self.queue_key = queue_key
        return redis.Redis(host=hostname, port=port, db=db)

    def add(self, data):
        self._client().lpush(self.queue_key, str(data))
        return True
