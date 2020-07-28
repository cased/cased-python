import pytest
import mock

import cased
from cased.data.reliability import (
    AbstractReliabilityBackend,
    RedisReliabilityBackend,
    ReliabilityEngine,
)

from cased.tests.util import mock_redis_backend_add, SimpleReliabilityBackend


class TestQuery:
    def test_reliability_engine_can_be_created(self):
        engine = ReliabilityEngine(backend=SimpleReliabilityBackend)
        assert isinstance(engine, ReliabilityEngine)

    def test_reliability_engine_class_delegates_to_a_configured_backend(self):
        engine = ReliabilityEngine(backend=SimpleReliabilityBackend)
        assert isinstance(engine.engine_backend, SimpleReliabilityBackend)

    def test_reliability_engine_cannot_be_created_without_backend(self):
        cased.reliability_backend = None
        with pytest.raises(Exception):
            ReliabilityEngine()

    def test_reliability_engine_can_be_configured_globally_with_string(self):
        cased.reliability_backend = "redis"
        engine = ReliabilityEngine()
        assert isinstance(engine.engine_backend, RedisReliabilityBackend)

    def test_reliability_engine_can_be_configured_globally_with_class(self):
        cased.reliability_backend = SimpleReliabilityBackend
        engine = ReliabilityEngine()
        assert isinstance(engine.engine_backend, SimpleReliabilityBackend)

    def test_abstract_reliability_backend_cannot_be_created(self):
        with pytest.raises(NotImplementedError):
            AbstractReliabilityBackend()

    def test_reliability_engine_backend_gets_automatic_name(self):
        cased.reliability_backend = "redis"
        engine = ReliabilityEngine()
        assert engine.engine_backend.name == "redis"

    def test_reliability_engine_backend_gets_automatic_name_with_class(self):
        cased.reliability_backend = SimpleReliabilityBackend
        engine = ReliabilityEngine()
        assert engine.engine_backend.name == "simple"

    def test_redis_reliability_backend_can_add_an_entry(self):
        with mock_redis_backend_add():
            engine = ReliabilityEngine(RedisReliabilityBackend)
            added = engine.add({"test": "data"})

            assert added is True

    def test_redis_reliability_backend_is_called_correctly(self):
        with mock_redis_backend_add():
            engine = ReliabilityEngine(RedisReliabilityBackend)
            engine.add({"test": "data"})

            cased.data.reliability.RedisReliabilityBackend.add.assert_called_with(
                {"test": "data"}
            )

    def test_redis_backend_key_can_be_configured(self):
        backend = RedisReliabilityBackend(queue_key="custom-key")
        assert backend.queue_key == "custom-key"

    def test_redis_client_has_defaults(self):
        backend = RedisReliabilityBackend()

        assert backend._configure_client() == (
            "localhost",
            6379,
            0,
            "cased:reliability_queue",
        )

    def test_redis_client_can_be_configured_globally(self):
        config = {"hostname": "myhost.com", "port": 4000, "db": 1}
        cased.redis_backend_config = config
        backend = RedisReliabilityBackend()

        assert backend._configure_client() == (
            "myhost.com",
            4000,
            1,
            "cased:reliability_queue",
        )
