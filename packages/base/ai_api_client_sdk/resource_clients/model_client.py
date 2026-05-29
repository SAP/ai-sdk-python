from ai_api_client_sdk.models.model_query_response import ModelQueryResponse
from ai_api_client_sdk.resource_clients.base_client import BaseClient


class ModelClient(BaseClient):
    """ModelClient is a class implemented for interacting with model related endpoints of the server. It
    implements the base class :class:`ai_api_client_sdk.resource_clients.base_client.BaseClient`
    """

    DEFAULT_SCENARIO_ID = "foundation-models"

    def query(
        self,
        resource_group: str = None,
    ) -> ModelQueryResponse:
        """Queries the models.

        :param resource_group: Resource Group which the request should be sent on behalf. Either this or a default
            resource group in the :class:`ai_api_client_sdk.ai_api_v2_client.AIAPIV2Client` should be specified,
            defaults to None
        :type resource_group: str
        :raises: class:`ai_api_client_sdk.exception.AIAPIInvalidRequestException` if a 400 response is received from the
            server
        :raises: class:`ai_api_client_sdk.exception.AIAPIAuthorizationException` if a 401 response is received from the
            server
        :raises: class:`ai_api_client_sdk.exception.AIAPIServerException` if a non-2XX response is received from the
            server
        :return: An object representing the response from the server
        :rtype: class:`ai_api_client_sdk.models.executable_query_response.ModelQueryResponse`
        """
        response_dict = self.rest_client.get(
            path=f"/scenarios/{ModelClient.DEFAULT_SCENARIO_ID}/models",
            resource_group=resource_group,
        )
        return ModelQueryResponse.from_dict(response_dict)
