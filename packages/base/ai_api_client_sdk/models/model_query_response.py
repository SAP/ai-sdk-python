from typing import Any, Dict, List

from ai_api_client_sdk.models.base_models import QueryResponse
from ai_api_client_sdk.models.model import Model


class ModelQueryResponse(QueryResponse):
    """The ModelQueryResponse object defines the response of the model query request
    :param resources: List of the models returned from the server
    :type resources: List[class:`ai_api_client_sdk.models.executable.Model`]
    :param count: Total number of the queried models
    :type count: int
    :param `**kwargs`: The keyword arguments are there in case there are additional attributes returned from server
    """

    def __init__(self, resources: List[Model], count: int, **kwargs):
        super().__init__(resources=resources, count=count, **kwargs)

    @staticmethod
    def from_dict(response_dict: Dict[str, Any]):
        """Returns a :class:`ai_api_client_sdk.models.executable_query_response.ModelQueryResponse` object, created
        from the values in the dict provided as parameter

        :param response_dict: Dict which includes the necessary values to create the object
        :type response_dict: Dict[str, Any]
        :return: An object, created from the values provided
        :rtype: class:`ai_api_client_sdk.models.executable_query_response.ModelQueryResponse`
        """
        response_dict["resources"] = [
            Model.from_dict(r) for r in response_dict["resources"]
        ]
        return ModelQueryResponse(**response_dict)
