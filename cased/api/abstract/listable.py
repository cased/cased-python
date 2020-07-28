from cased.api.abstract import CasedAPIResource
from cased.api.abstract.results_list import ResultsList
from cased.http import Requestor
import cased


class ListableResource(CasedAPIResource):
    @classmethod
    def list(cls, **params):
        url = cls.class_url() + "/"
        data = {}

        limit = params.get("limit") or 25
        page = params.get("page", None)
        policy = params.get("policy", None)
        search = params.get("search", None)
        variables = params.get("variables", None)

        if page:
            data["page"] = page

        if search:
            data["phrase"] = search

        data["per_page"] = limit

        if variables:
            if not isinstance(variables, dict):
                raise TypeError("`variables` parameter must of type `dict`")

            for key, value in variables.items():
                param_key = "variables[{}]".format(key)
                data[param_key] = value

        if params.get("api_key"):
            # Respect any api_key given on a per-request basis
            pass
        elif policy:
            # A policy was given; so use that key
            params["api_key"] = cased.policy_keys.get(policy)
        else:
            # Nothing to do, we'll use the default policy key
            pass

        requestor = Requestor.policy_requestor(**params)

        response = requestor.request("get", url, data=data)
        return ResultsList(response, cls.resource_class())
