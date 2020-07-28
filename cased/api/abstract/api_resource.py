from cased.http import Requestor


class CasedAPIResource:
    @classmethod
    def fetch(cls, resource_id, **params):
        """
        Fetch the resource represented by resource_id. Any
        APIResource has a fetch function.
        """
        requestor = Requestor.policy_requestor(**params)
        url = cls.class_url() + "/" + resource_id
        response = requestor.request("get", url)
        return response

    @classmethod
    def class_url(cls):
        if cls == CasedAPIResource:
            raise NotImplementedError(
                """class_url() called on abstract CasedAPIResource.
                 This is likely a bug in the Cased library."""
            )

        base = cls.RESOURCE_NAME
        return "/{}".format(base)

    @classmethod
    def resource_class(cls):
        if cls == CasedAPIResource:
            raise NotImplementedError(
                """resource_class() called on abstract CasedAPIResource.
                 This is likely a bug in the Cased library."""
            )

        return cls.klass()
