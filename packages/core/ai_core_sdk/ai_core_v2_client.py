from ai_core_sdk.helpers.logging import get_logger
from typing import Callable
import os

from ai_core_sdk.helpers import is_within_aicore
from ai_core_sdk.resource_clients import (
    AIAPIV2Client,
    ArtifactClient,
    ConfigurationClient,
    DeploymentClient,
    ExecutableClient,
    ExecutionClient,
    RestClient,
    ScenarioClient,
    ResourceGroupsClient,
    MetaClient,
    ModelClient,
)
from ai_core_sdk.resource_clients.applications_client import ApplicationsClient
from ai_core_sdk.resource_clients.docker_registry_secrets_client import DockerRegistrySecretsClient
from ai_core_sdk.resource_clients.internal_rest_client import InternalRestClient
from ai_core_sdk.resource_clients.metrics_client import MetricsCoreClient
from ai_core_sdk.resource_clients.object_store_secrets_client import ObjectStoreSecretsClient
from ai_core_sdk.resource_clients.kpi_client import KpiClient
from ai_core_sdk.resource_clients.repositories_client import RepositoriesClient
from ai_core_sdk.resource_clients.secrets_client import SecretsClient
from ai_core_sdk.helpers.constants import Timeouts
from ai_core_sdk.credentials import fetch_credentials


class AICoreV2Client:
    """The AICoreV2Client is the class implemented to interact with the AI Core endpoints. The user can use its
    attributes corresponding to the resources, for interacting with endpoints related to that resource. (i.e.,
    aicoreclient.scenario)

    :param base_url: Base URL of the AI Core. Should include the base path as well. (i.e., "<base_url>/lm/scenarios"
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
    :param client_type: The client type which will be sent in the User-Agent header of the requests, defaults to
        "AI Core Python SDK"
    :type client_type: str, optional
    :param \\**kwargs:
        * *read_timeout* (int): Read timeout for requests in seconds, defaults to 60s
        * *connect_timeout* (int): Connect timeout for requests in seconds, defaults to 60s
        * *num_request_retries* (int): Number of retries for failing requests with http status code 429, 500, 502, 503 or 504, defaults to 10
    """
    logger = get_logger()

    # pylint: disable=too-many-arguments
    def __init__(self, base_url: str, auth_url: str = None, client_id: str = None, client_secret: str = None,
                 cert_str: str = None, key_str: str = None, cert_file_path: str = None, key_file_path: str = None,
                 token_creator: Callable[[], str] = None, resource_group: str = None,
                 client_type: str = "AI Core Python SDK",
                 **kwargs):
        self.base_url: str = base_url
        ai_api_base_url = f'{base_url}/lm'
        token_creator = AIAPIV2Client._create_token_creator_if_does_not_exist(
            token_creator=token_creator, auth_url=auth_url, client_id=client_id, client_secret=client_secret,
            cert_str=cert_str, key_str=key_str, cert_file_path=cert_file_path, key_file_path=key_file_path)

        read_timeout = kwargs.get('read_timeout', Timeouts.READ_TIMEOUT.value)
        connect_timeout = kwargs.get('connect_timeout', Timeouts.CONNECT_TIMEOUT.value)
        num_request_retries = kwargs.get('num_request_retries', Timeouts.NUM_REQUEST_RETRIES.value)

        ai_api_v2_client = AIAPIV2Client(base_url=ai_api_base_url, token_creator=token_creator,
                                         resource_group=resource_group, read_timeout=read_timeout,
                                         connect_timeout=connect_timeout, num_request_retries=num_request_retries,
                                         client_type=client_type)

        self.rest_client: RestClient = RestClient(base_url=base_url, get_token=token_creator,
                                                  resource_group=resource_group, read_timeout=read_timeout,
                                                  connect_timeout=connect_timeout,
                                                  num_request_retries=num_request_retries,
                                                  client_type=client_type)
        self.artifact: ArtifactClient = ai_api_v2_client.artifact
        self.configuration: ConfigurationClient = ai_api_v2_client.configuration
        self.deployment: DeploymentClient = ai_api_v2_client.deployment
        self.executable: ExecutableClient = ai_api_v2_client.executable
        self.execution: ExecutionClient = ai_api_v2_client.execution
        self.resource_groups: ResourceGroupsClient = ai_api_v2_client.resource_groups
        self.meta: MetaClient = ai_api_v2_client.meta
        self.model: ModelClient = ai_api_v2_client.model
        # If the environment variables have AICORE_EXECUTION_ID and AICORE_TRACKING_ENDPOINT,
        # it indicates the sdk is used within the training pod
        # Initiating an internal rest client if within the training pod
        # Else initiating the rest client from ai_api_v2_client
        if is_within_aicore():
            self.metrics: MetricsCoreClient = MetricsCoreClient(
                rest_client=InternalRestClient(
                    client_type=client_type,
                    read_timeout=read_timeout,
                    connect_timeout=connect_timeout,
                    num_request_retries=num_request_retries,
                ),
                execution_id=os.getenv("AICORE_EXECUTION_ID"),
            )
        else:
            self.metrics: MetricsCoreClient = MetricsCoreClient(rest_client=ai_api_v2_client.rest_client)
        self.scenario: ScenarioClient = ai_api_v2_client.scenario
        self.docker_registry_secrets: DockerRegistrySecretsClient = DockerRegistrySecretsClient(
            rest_client=self.rest_client)
        self.applications: ApplicationsClient = ApplicationsClient(rest_client=self.rest_client)
        self.object_store_secrets: ObjectStoreSecretsClient = ObjectStoreSecretsClient(rest_client=self.rest_client)
        self.secrets: SecretsClient = SecretsClient(rest_client=self.rest_client)
        self.kpis: KpiClient = KpiClient(rest_client=self.rest_client)
        self.repositories: RepositoriesClient = RepositoriesClient(rest_client=self.rest_client)

    @staticmethod
    def from_env(profile_name: str = None,
                 **kwargs):
        """Alternative way to create an AICoreV2Client object.
        Parameters for base_url, auth_url, client_id, client_secret, x.509 credentials (either as file path or string)
        and resource_group can be passed as keyword or are pulled from environment variables.
        It is also possible to use a profile, which is a json file in the config directory. The profile name can be
        passed as keyword or is pulled from the environment variable AICORE_PROFILE. If no profile is specified,
        the default profile is used.
        A specific path to a config, that should be used, can be set via the environment variable AICORE_CONFIG.
        The hierarchy of precedence is:
        1. keyword argument
        2. environment variable
        3. configuration file
        4. value from VCAP_SERVICES environment variable, if exists

        :param profile_name: name of the profile to use, defaults to None. If None is passed, the profile is read from
            the environment variable AICORE_PROFILE. If this is not set, the default profile is used.
            The default profile is read from $AICORE_HOME/config.json.
        :type profile_name: optional, str
        **kwargs: check the parameters of the class constructor
        """
        env_credentials = fetch_credentials(profile=profile_name, **kwargs)

        kwargs.update(env_credentials)
        return AICoreV2Client(**kwargs)
