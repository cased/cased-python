from cased.api.abstract import ListableResource, CreatableResource, DeletableResource
from cased.http import Requestor


class Export(CreatableResource):
    RESOURCE_NAME = "exports"

    @classmethod
    def download(cls, export_id, **params):
        requestor = Requestor.policy_requestor(**params)
        url = cls.class_url() + "/{}/download".format(export_id)

        return requestor.request("get", url)

    @classmethod
    def klass(cls):
        return cls
