# ===================== cased-python ==========================
import os
from cased.data.context import Context

# =============================================================
# Package settings
# =============================================================
VERSION = "0.4.0"
APP_NAME = "Cased"


# =============================================================
# Keys
# =============================================================


def _get_env_publish_key():
    return os.getenv("CASED_PUBLISH_KEY")


def _get_env_policy_key():
    return os.getenv("CASED_POLICY_KEY")


policy_key = None or _get_env_policy_key()  # Default policy key

policy_keys = {}  # Dict of policy keys, mapped as policy key name => key

publish_key = None or _get_env_publish_key()  # Key used to publish events


# =============================================================
# Client configuration
# =============================================================

client_id = None

api_base = "https://api.cased.com"
publish_base = "https://publish.cased.com"

disable_publishing = False

# When enabled, clear the Context data after publishing.
clear_context_after_publishing = False

# When enabled, this setting redacts any configured sensitive data prior
# to publishing of event. Sensitive data characters will be replaced with `X`.
redact_before_publishing = False

# Whether or not to raise an exception, or just log, on errors during publish
raise_on_publish_errors = True

# Allow extra user-agent data
extra_ua_data = None

# =============================================================
# Additional publishers
# =============================================================

additional_publishers = []


def add_publisher(publisher):
    additional_publishers.append(publisher)


def remove_publisher(publisher):
    additional_publishers.remove(publisher)


# =============================================================
# Logging
# =============================================================

log_level = None  # ["debug", "info", "error"]


# =============================================================
# Reliability backends
# =============================================================

reliability_backend = None  # ['redis', YourCustomBackend]
warn_if_no_reliability_backend = False


# =============================================================
# Data plugins
# =============================================================

from cased.plugins import CasedDefaultPlugin  # noqa

data_plugins = [CasedDefaultPlugin]


def add_plugin(plugin):
    data_plugins.append(plugin)


def remove_plugin(plugin):
    data_plugins.remove(plugin)


# =============================================================
# Sensitive data handlers
# =============================================================

sensitive_data_handlers = []


def add_handler(handler):
    sensitive_data_handlers.append(handler)


def clear_handlers():
    sensitive_data_handlers.clear()


delete_pii = False


# =============================================================
# Sensitive fields
# =============================================================

sensitive_fields = set()


def add_sensitive_field(field):
    sensitive_fields.add(field)


def clear_sensitive_fields():
    sensitive_fields.clear()


# =============================================================
# Context
# =============================================================

context = Context


# =============================================================
# API Resources
# =============================================================

from cased.api import *  # noqa
