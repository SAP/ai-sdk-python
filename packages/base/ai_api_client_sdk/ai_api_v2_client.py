import os
from typing import Callable

from ai_api_client_sdk.exception import AIAPIAuthenticatorException
from ai_api_client_sdk.helpers import _is_all_none
from ai_api_client_sdk.helpers.authenticator import Authenticator
from ai_api_client_sdk.helpers.constants import SKIP_AUTH_ENV_VAR, Timeouts
from ai_api_client_sdk.helpers.rest_client import RestClient
from ai_api_client_sdk.resource_clients import (
    ArtifactClient,
    ConfigurationClient,
    DeploymentClient,
    ExecutableClient,
    ExecutionClient,
    ExecutionScheduleClient,
    HealthzClient,
    MetaClient,
    MetricsClient,
    ModelClient,
    ResourceGroupsClient,
    ScenarioClient,
)

AUTH_PARAM_ERROR_MESSAGE = """
For authorization please provide either one of the following options:
1. token_creator
2. auth_url, client_id and one of the following options:
    a. client_secret
    b. cert_str & key_str
    c. cert_file_path & key_file_path
"""


class AIAPIV2Client:
    """The AIAPIV2Client is the class implemented to interact with the AI API server. The user can use its attributes
    corresponding to the resources, for interacting with endpoints related to that resource. (i.e.,
    aiapiv2client.scenario)

    :param base_url: Base URL of the AI API server. Should include the base path as well. (i.e., "<base_url>/scenarios"
        should work)
    :type base_url: str
    :param auth_url: URL of the authorization endpoint. Should be the full URL (including /oauth/token), defaults to
        None
    :type auth_url: str, optional
    :param client_id: client id to be used for authorization, defaults to None
    :type client_id: str, optional
    :param client_secret: client secret to be used for authorization, defaults to None
    :type client_secret: str, optional
    :param cert_str: certificate file content, needs to be provided alongside the key_str parameter, defaults to None
    :type cert_str: str, optional
    :param key_str: key file content, needs to be provided alongside the cert_str parameter, defaults to None
    :type key_str: str, optional
    :param cert_file_path: path to the certificate file, needs to be provided alongside the key_file_path parameter,
        defaults to None
    :type cert_file_path: str, optional
    :param key_file_path: path to the key file, needs to be provided alongside the cert_file_path parameter,
        defaults to None
    :type key_file_path: str, optional
    :param token_creator: the function which returns the Bearer token, when called. Either this, or
        auth_url & client_id & client_secret should be specified, defaults to None
    :type token_creator: Callable[[], str], optional
    :param resource_group: The default resource group which will be used while sending the requests to the server. If
        not set, the resource_group should be specified with every request to the server, defaults to None
    :type resource_group: str, optional
    :param read_timeout: Read timeout for requests in seconds, defaults to 60s
    :type read_timeout: int
    :param connect_timeout: Connect timeout for requests in seconds, defaults to 60s
    :type connect_timeout: int
    :param num_request_retries: Number of retries for failing requests with http status code 429, 500, 502, 503 or 504,
        defaults to 60s
    :type num_request_retries: int
    :param client_type: Client type header to be sent in the request, defaults to 'AI API Python SDK'
    :type client_type: str
    """

    @staticmethod
    def _create_token_creator_if_does_not_exist(token_creator, auth_url, client_id, client_secret, cert_str, key_str,
                                                cert_file_path, key_file_path):
        if token_creator:
            if not _is_all_none(auth_url, client_id, client_secret, cert_str, key_str, cert_file_path, key_file_path):
                raise AIAPIAuthenticatorException(error_message=AUTH_PARAM_ERROR_MESSAGE)
            return token_creator
        try:
            return Authenticator(auth_url=auth_url, client_id=client_id, client_secret=client_secret, cert_str=cert_str,
                                 key_str=key_str, cert_file_path=cert_file_path, key_file_path=key_file_path).get_token
        except TypeError as te:
            if any(x in te.__str__() for x in ['auth_url', 'client_id']):
                raise AIAPIAuthenticatorException(error_message=AUTH_PARAM_ERROR_MESSAGE)
            raise te
        except AIAPIAuthenticatorException:
            raise AIAPIAuthenticatorException(error_message=AUTH_PARAM_ERROR_MESSAGE)

    def __init__(self, base_url: str, auth_url: str = None, client_id: str = None, client_secret: str = None,
                 cert_str: str = None, key_str: str = None, cert_file_path: str = None, key_file_path: str = None,
                 token_creator: Callable[[], str] = None, resource_group: str = None,
                 connect_timeout=Timeouts.CONNECT_TIMEOUT.value,
                 num_request_retries=Timeouts.NUM_REQUEST_RETRIES.value,
                 **kwargs):
        read_timeout = kwargs.get('read_timeout', Timeouts.READ_TIMEOUT.value)
        client_type = kwargs.get('client_type', 'AI API Python SDK')

        self.base_url: str = base_url
        if os.environ.get(SKIP_AUTH_ENV_VAR, '').lower() != 'true':
            token_creator = self._create_token_creator_if_does_not_exist(
                token_creator=token_creator, auth_url=auth_url, client_id=client_id, client_secret=client_secret,
                cert_str=cert_str, key_str=key_str, cert_file_path=cert_file_path, key_file_path=key_file_path)
        self.rest_client: RestClient = RestClient(base_url=base_url, get_token=token_creator,
                                                  resource_group=resource_group, read_timeout=read_timeout,
                                                  connect_timeout=connect_timeout,
                                                  num_request_retries=num_request_retries,
                                                  client_type=client_type)
        self.artifact: ArtifactClient = ArtifactClient(rest_client=self.rest_client)
        self.configuration: ConfigurationClient = ConfigurationClient(rest_client=self.rest_client)
        self.deployment: DeploymentClient = DeploymentClient(rest_client=self.rest_client)
        self.executable: ExecutableClient = ExecutableClient(rest_client=self.rest_client)
        self.execution: ExecutionClient = ExecutionClient(rest_client=self.rest_client)
        self.execution_schedule: ExecutionScheduleClient = ExecutionScheduleClient(rest_client=self.rest_client)
        self.healthz: HealthzClient = HealthzClient(rest_client=self.rest_client)
        self.metrics: MetricsClient = MetricsClient(rest_client=self.rest_client)
        self.model: ModelClient = ModelClient(rest_client=self.rest_client)
        self.scenario: ScenarioClient = ScenarioClient(rest_client=self.rest_client)
        self.meta: MetaClient = MetaClient(rest_client=self.rest_client)
        admin_rest_client = RestClient(base_url=base_url[:-3], get_token=token_creator, resource_group=resource_group)
        self.resource_groups: ResourceGroupsClient = ResourceGroupsClient(rest_client=admin_rest_client)
