from cased.api.abstract import ListableResource, CreatableResource, DeletableResource


class Policy(ListableResource, CreatableResource, DeletableResource):
    RESOURCE_NAME = "policies"

    @classmethod
    def klass(cls):
        return cls
