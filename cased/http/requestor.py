import cased
import requests

from cased import errors

from cased.http import HTTPClient


class Requestor:
    def __init__(self, client=HTTPClient, *args, **kwargs):
        self.api_base = kwargs.get("api_base") or cased.api_base
        self.api_key = kwargs.get("api_key")

        if self.api_key is None:
            raise Exception(
                """No API key provided. Set a policy key using
                cased.policy_key = <API-KEY>, or set a publish key for
                publishing, or supply a key with the request. See
                https://docs.cased.com for more information."""
            )

        self.client = client

    @classmethod
    def policy_requestor(cls, **params):
        if not params.get("api_key"):
            params["api_key"] = cased.policy_key

        return Requestor(**params)

    @classmethod
    def publish_requestor(cls, **params):
        if not params.get("api_base"):
            params["api_base"] = cased.publish_base

        if not params.get("api_key"):
            params["api_key"] = cased.publish_key

        return Requestor(**params)

    def request(self, method, url, data=None):
        if self.api_key is None:
            raise errors.AuthenticationError(
                """No API key provided. Set a policy key using
                cased.policy_key = <API-KEY>, or set a publish key for
                publishing, or supply a key with the request. See
                https://docs.cased.com for more information."""
            )

        absolute_url = self.api_base + url
        return self.client.make_request(method, absolute_url, self.api_key, data)
