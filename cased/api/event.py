import uuid
from datetime import datetime

import cased
import requests
from deepmerge import always_merger


from cased.http import Requestor
from cased.util import log_info, log_error

from cased.api.abstract import ListableResource
from cased.api.abstract.results_list import ResultsList
from cased.data.reliability import ReliabilityEngine, ReliabilityEngineError
from cased.data.sensitive import SensitiveDataProcessor
from cased.data.query import Query


class Event(ListableResource):
    RESOURCE_NAME = "events"

    @classmethod
    def publish(cls, data, **params):
        if cased.disable_publishing:
            return None

        requestor = Requestor.publish_requestor(**params)
        publish_data = data.copy()

        # Using the plugin system, add any data from plugins that have been configured
        data_plugins = getattr(cased, "data_plugins", [])
        for plugin in data_plugins:
            instance = plugin(publish_data)
            additions = instance.additions()
            publish_data.update(additions)

        # Include context data, overriding it with any local publish data
        current_context = cased.context.current()
        always_merger.merge(current_context, publish_data)

        # Update the .cased with any PII ranges
        processor = SensitiveDataProcessor(current_context)
        final_publish_data = processor.process()

        # Add the item to a ReliabilityEngine backend. The backend can be configured
        # with a "backend" keyword arg passed to publish(), or with the global config.
        # By default, we try/except just in case the user misconfigured their ReliabilityEngine:
        # we'd rather still send the audit data then fail here. But we do log a message.
        # Additionally, if a ReliabilityBackend is not set, we will (optionally) log a warning.
        try:
            if "backend" in params:
                engine = ReliabilityEngine(backend=params["backend"])
                engine.add(publish_data)
            elif cased.reliability_backend:
                engine = ReliabilityEngine(backend=cased.reliability_backend)
                engine.add(publish_data)
            else:
                if cased.warn_if_no_reliability_backend:
                    log_info("No reliability backend has been set")
        except ReliabilityEngineError as e:
            log_info(
                """Reliability backend is misconfigured.
                Please check configuration. Client will still
                send audit data to Cased. Error: {}""".format(
                    e
                )
            )

        try:
            # Send to Cased
            response = requestor.request("post", "/", final_publish_data)
            log_info("Sent to Cased: " + str(final_publish_data))

            # Publish the item to any additional publishers
            additional_publishers = cased.additional_publishers
            for publisher in additional_publishers:
                try:
                    publisher.publish(final_publish_data)
                except AttributeError:
                    raise PublisherException("Publisher must implement publish()")

        except Exception as e:
            log_error(e)
            if cased.raise_on_publish_errors:
                raise
        finally:
            if cased.clear_context_after_publishing:
                cased.context.clear()

        return response

    @classmethod
    def list_by_action(cls, action, **params):
        """
        List an audit trail by action
        """
        params["search"] = Query.make_phrase_from_dict({"action": action})
        return cls.list(**params)

    @classmethod
    def list_by_actor(cls, actor, **params):
        """
        List an audit trail by an actor
        """
        params["search"] = Query.make_phrase_from_dict({"actor": actor})
        return cls.list(**params)

    @classmethod
    def klass(cls):
        return cls


class PublisherException(Exception):
    pass
