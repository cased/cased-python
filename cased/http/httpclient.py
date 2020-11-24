import cased
import requests

from cased.util import log_debug


class HTTPClient:
    @classmethod
    def make_request(cls, method, url, api_key, data=None):

        user_agent = "cased-python/{}".format(cased.VERSION)

        if cased.extra_ua_data:
            user_agent = user_agent + " ({})".format(cased.extra_ua_data)

        headers = {
            "Authorization": "Bearer " + api_key,
            "User-Agent": user_agent,
        }

        if method == "get":
            res = requests.get(url, params=data, headers=headers)
        elif method == "post":
            res = requests.post(url, json=data, headers=headers)
        elif method == "put":
            res = requests.put(url, json=data, headers=headers)
        elif method == "patch":
            res = requests.patch(url, json=data, headers=headers)
        elif method == "head":
            res = requests.head(url, headers=headers)
        elif method == "delete":
            res = requests.delete(url, headers=headers)
        else:
            raise Exception(
                """Unsupported method given. This is likely a bug in the
                Cased API library."""
            )

        log_debug(
            "Request sent. URL: {} | Params: {} | Headers: {}".format(
                url, str(data), str(headers)
            )
        )

        return res
