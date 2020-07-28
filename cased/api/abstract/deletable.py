from cased.api.abstract import CasedAPIResource
from cased.http import Requestor


class DeletableResource(CasedAPIResource):
    @classmethod
    def delete(cls, resource_id, **params):
        requestor = Requestor.policy_requestor(**params)
        url = cls.class_url() + "/" + resource_id
        response = requestor.request("delete", url)
        return response
