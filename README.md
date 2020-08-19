# cased-python

`cased-python` is the official Python client for [Cased](https://cased.com), a web service for adding audit trails to any application in minutes. This Python client makes it easy to record and query your Cased audit trail events. The client also includes a robust set of features to mask PII, add client-side resilience, and automatically augment events with more data.

![CI Badge](https://github.com/cased/cased-python/workflows/cased-python/badge.svg) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

| Contents                         |
| :------------------------------- |
| [Installation](##installation)   |
| [Configuration](##configuration) |
| [How To Guide](##usage-guide)    |
| [Tests](##tests)                 |

## Installation

The recommended way to install the Cased library module is to use `pipenv` (or just pip itself):

```
pipenv install cased
```

You can also use the classic:

```
python3 setup.py install
```

## Configuration

The client can be configured using environment variables or initialized programmatically.

To send events, you use a **publish key**. The Python client will look for an envionment variable `CASED_PUBLISH_KEY`.
This key can be found in your [Cased](https://cased.com) dashboard.

The API key can also be provided programatically, and will take precedence over an env variable.
Example environment variable usage:

```
$ CASED_PUBLISH_KEY="publish_test_c260ffa178db6d5953f11f747ecb7ee3" python app.py
```

Or programmatically:

```python
import cased
cased.publish_key = "publish_test_c260ffa178db6d5953f11f747ecb7ee3"
```

You can also send your API key with each request:

```python
import cased

cased.Event.publish({"action": "user.login"}, api_key="publish_test_c260ffa178db6d5953f11f747ecb7ee3")
```

(Setting an API key on a request takes precedence over both the global setting and the environmental variable setting).

To read events, you use a **policy key**. Set a default policy key (i.e., a key that will automatically be used unless
another is given):

```
$ CASED_POLICY_KEY="policy_test_f764a5f252aaca986b0526b42a6f7e95"
```

Or programatically:

```python
cased.policy_key = "policy_test_f764a5f252aaca986b0526b42a6f7e95"
```

For more advanced configuration of policy keys, see the section _Policy Keys_ below.


## How To Guide

Record your first audit trail event using the `publish()` function on the `Event` class.

```python
import cased

cased.Event.publish({
  event: "user.login",
  location: "130.25.167.191",
  request_id: "e851b3a7-9a16-4c20-ac7f-cbcdd3a9c183",
  server: "app.fe1.disney.com",
  session_id: "e2bd0d0e-165c-4e2a-b40b-8e2997fd7915",
  user_agent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
  user_id: "User;1",
  user: "mickeymouse",
})
```

### Fetch an event

All API classes have `fetch` functions so you can retrieve a JSON representation of any object. For simple usage, pass
the object's id. Additionally, you can pass a policy `api_key` if you haven't already set a default one.

```python
import cased

cased.Event.fetch("e19a2032-f841-426c-8a13-5a938e7934a3", api_key="policy_test_f764a5f252aaca986b0526b42a6f7e95")
```

and you'll get back the event.

### Result lists and pagination

Many objects, such as `Event` and `Policy` have `list()` functions. These functions return `ResultsList` objects of
paginated results, plus pagination metadata and useful functions. For example:

```python

events = cased.Event.list()
events.results # Get the list of the first page of results
```

By default, `list()` returns 25 items at a time. This can be adjusted,
with a maximum of 50 items.

```python
events = cased.Event.list(limit=10)
```

You can get metadata:

```python
events.total_count # Total count of objects
events.total_pages # Total number of pages
```

You can also get urls and page numbers to paginate the results.

```python
events.next_page_url
# > https://api.cased.com.com/api/events?page=3

events.next_page
#> 3

events.last_page_url
# > https://api.cased.com.com/api/events?page=20

events.last_page
# > 20
```

It is much easier to use the iterators provided by this library.

```python
events = cased.Event.list()
iterator = events.page_iter()
for item in iterator:
  print(item)
```

`page_iter()` is generator that yields a results item per iteration. So it can be used to automatically run through paginated results in an efficient way. Like any generator it works with the ordinary `for..in`, and with `next()`.

`page_iter()` is available for any resource class that has a `list()` function.

### Control your returned events with policy variables

You can control what events you get back from `list()` by using the `variables` parameter.
`variables` is a `dict` of fields which are then applied to a policy. For example:

```python
events = cased.Event.list(variables={"team_id": "team-123"})
```

You can set multiple variables:

```python
events = cased.Event.list(variables={"team_id": "team-123", "organization_id": "org-abc"})
```

Additionally, you can further limit and filter your results by using a _search phrase_:

```python
events = cased.Event.list(search="user:jill", variables={"team_id": "team-123"})
```

### More for list()

You can use some additional convenience functions:

```python
Event.list_by_actor("jill")

Event.list_by_action("invite.created")
```

Pass in policy variables as well:

```python
Event.list_by_actor("jill", variables={"team_id": "team-123"})
```

You can easily build a search query phrase from a Python dictionary, and then pass
that to `list()`:

```python
from cased import Query

data = {"actor": "jill", "location": "Austria"}
my_query = Query.make_phrase_from_dict(data)

cased.Event.list(search=my_query)
```

### Policy Keys

You may use multiple policies to read data from Cased. Each policy has its own associated API key. To make this easy, the library provides a `cased.policy_keys` configuration option, which lets you map arbitrary policy names to keys.

```python
import cased

cased.policies = {
  "primary": "policy_live_1dQpY8bBgEwdpmdpVrrtDzMX4fH",
  "secondary": "policy_live_1dSHQRurWX8JMYMbkRdfzVoo62d"
}
```

Then use, with, for example, a `list()` operation.

```python
Event.list(policy="primary")
```

You can still mix with policy variables, of course:

```python
Event.list(policy="primary", variables={"team_id": "team-123"})
```

### `ReliabilityEngine` and Backends

A `ReliabilityEngine` adds extra resilience to the client by writing audit entries to a
local datastore for later processing. This can be useful if, for whatever reason, your client
is unable to reached Cased. A `ReliabilityEngine` can queue up events for later sending to Cased.

A `ReliabilityEngine` has a `ReliabilityBackend` — right now
this library includes a Redis implementation. A backend implements `add()`, which adds data to
a datastore for later processing. You can implement your own by
subclassing `cased.data.reliability.AbstractReliabilityBackend`.

It's very easy to set one up. You can set one globally using either a default string name (just 'redis'
currently), or by using a class.

```
cased.reliability_backend = "redis"
```

or set a custom class:
```python
cased.reliability_backend = MyCustomClass
```

All publish events will now also write events to that reliability backend. We recommend using a reliability
backend, although it is not required.

You can also set a backend on a per-request basis, by passing a `backend` keyword arg to `Event.publish()`

## Data Plugins

A `DataPlugin` enriches your audit events with any arbitrary additional data.
Define one easily by subclassing `cased.plugins.DataPlugin` and implementing
an `additions` function. Then return a `dict` of additional data and that data will
automatically be sent to Cased along with your audit event.

When implementing a plugin, you can access the audit entry itself with `self.data`,
in case your plugin needs to do some processing based on the audit entry data.

```python
cased.add_plugin(MyCustomPlugin)
```

Here's an example — the default plugin that ships with this library:

```python
class CasedDefaultPlugin(DataPlugin):
    def additions(self):
        return {
            "cased_id": uuid.uuid4().hex,
            "timestamp": str(
                datetime.now(timezone.utc).isoformat(timespec="microseconds")
            ),
        }
```

### Sensitive Data

You can mark audit entry fields as _sensitive_ to mask PII. Just use the global set:

```python
cased.sensitive_fields = {"username", "address"}
```

Any field, in any audit event, that matches one of those key name will be marked as
sensitive when sent to Cased.

You can also mark _patterns_ in your audit trail dail as sensitive_in order to mask PII. To do so,
create a `SensitiveDataHandler`:

```python
handler = SensitiveDataHandler(label="username", pattern=r"@([A-Za-z0-9_]+)
```

A sensitive data handler includes a `label`, which makes it easy to identify what kind of data is being masked.
Additionally, it includes a `pattern`, which is a regular expression matching a pattern you want to mark as sensitive.

Add it globally:

```python
cased.add_handler(handler)
```

Now any data you send that matches that pattern with will be marked as PII when sent to Cased.

### Disable Publishing

You may want to completely prevent events from being published (perhaps for testing purposes). To do so,
just set:

```python
cased.disable_publishing == True
```

## Logging

You can enable logging for useful `info` and `debug` messages:

```python
import cased
cased.log = 'debug'
```

Use through Python's native logging:

```python
import logging
logging.basicConfig()
logging.getLogger('cased').setLevel(logging.DEBUG)
```

## Contributing

Contributions to this library are welcomed and a complete test suite is available. Tests can be run locally using the following command:

```
pytest
```

Code formatting and linting is provided by [Black](https://black.readthedocs.io/en/stable/) and [Flake8](https://flake8.pycqa.org/en/latest/) respectively, so you may want to install them locally.

