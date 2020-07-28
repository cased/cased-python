from cased.api.abstract import CasedAPIResource
from cased.http import Requestor


class CreatableResource(CasedAPIResource):
    @classmethod
    def create(cls, **params):
        requestor = Requestor.policy_requestor(**params)
        data = params
        url = cls.class_url() + "/"
        response = requestor.request("post", url, data)
        return response
