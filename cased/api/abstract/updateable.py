from cased.api.abstract import CasedAPIResource
from cased.http import Requestor


class UpdateableResource(CasedAPIResource):
    @classmethod
    def update(cls, resource_id, **params):
        requestor = Requestor.policy_requestor(**params)
        data = params
        url = cls.class_url() + "/" + resource_id
        response = requestor.request("put", url, data)
        return response
