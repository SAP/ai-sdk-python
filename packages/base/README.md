# SAP Cloud SDK for AI (Python): Base Client for AI API

The SDK formerly known as *AI API Client SDK* was rebranded.

Use the new package name to install the SDK:
```
pip install sap-ai-sdk-base 
```
The class names have not changed i.e., you can continue to use existing code.

Everything in ai_api_client_sdk folder will be packaged in the library.

The main client class is the [AIAPIV2Client](ai_api_client_sdk/ai_api_v2_client.py). Each instance of AIAPIV2Client 
has resource clients as properties. The resource client implementations can be found in folder [resource_clients](ai_api_client_sdk/resource_clients). 
The resources, response types etc. are represented by model classes. These can be found in folder [models](ai_api_client_sdk/models).

Renovate is set up for this repository. For further information, take a look at the [documentation in ml-api-facade](https://github.wdf.sap.corp/AI/ml-api-facade/blob/master/docs/renovate.md).

## Usage

The user can use the library by creating an instance of AIAPIV2Client class. There are some required and optional 
parameters for the constructor of AIAPIV2Client class: 

- `base_url` (string) (required): The base URL of AI API. (i.e. https://api.ai.nonexistingcluster.com/v2/lm)
- `token_creator` (optional) (Callable): This should be a function which returns a token for authorization. Either this 
                                       function or auth_url, client_id and client_secret should be provided.
- `auth_url`: URL for creating the authorization token (i.e. https://blabla.authentication.sap.hana.ondemand.com/oauth/token)
- `client_id` (optional): clientid for xsuaa authentication
- `client_secret`(optional): clientsecret for xsuaa authentication
- `cert_str`(optional): certificate file content, needs to be provided alongside the key_str parameter
- `key_str` (optional): key file content, needs to be provided alongside the cert_str parameter
- `cert_file_path` (optional): path to the certificate file, needs to be provided alongside the key_file_path parameter
- `key_file_path` (optional): path to the key file, needs to be provided alongside the cert_file_path parameter
- `resource_group` (string) (optional): if provided, this will be used as default resource group id for requests to the AI API. 
                                      The user can still provide resource_group with every request to the AI API, 
                                      and that will override this one.

The AIAPIV2Client will have a property per resource (each one is an instance of a resource_client):

- `artifact` (an instance of [ArtifactClient](ai_api_client_sdk/resource_clients/artifact_client.py))
- `configuration` (an instance of [ConfigurationClient](ai_api_client_sdk/resource_clients/configuration_client.py))
- `deployment` (an instance of [DeploymentClient](ai_api_client_sdk/resource_clients/deployment_client.py))
- `executable` (an instance of [ExecutableClient](ai_api_client_sdk/resource_clients/executable_client.py))
- `execution` (an instance of [ExecutionClient](ai_api_client_sdk/resource_clients/execution_client.py))
- `healthz` (an instance of [HealthzClient](ai_api_client_sdk/resource_clients/healthz_client.py))
- `metrics` (an instance of [MetricsClient](ai_api_client_sdk/resource_clients/metrics_client.py))
- `scenario` (an instance of [ScenarioClient](ai_api_client_sdk/resource_clients/scenario_client.py))
- `resource_groups` (an instance of [ResourceGroupsClient](ai_api_client_sdk/resource_clients/resource_groups_client.py))

Each resource client has these functions (if supported for that resource) to send requests to the AI API:

- create(*args, **kwargs): creates a resource
- delete(*args, **kwargs): deletes a resource
- get(*args, **kwargs): gets a single resource
- modify(*args, **kwargs): patches a resource 
- query(*args, **kwargs): queries multiple resources

Example:

```python

from ai_api_client_sdk.ai_api_v2_client import AIAPIV2Client

ai_api_v2_client = AIAPIV2Client(
    base_url="<BASE_URL>", 
    auth_url="<AUTH_URL>", 
    client_id="<CLIENT_ID>",
    client_secret="<CLIENT_SECRET>", 
    resource_group="<RESOURCE_GROUP_ID>"
)

scenario = ai_api_v2_client.scenario.get(scenario_id="<SCENARIO_ID>")
```

## Tests

The [unit tests](tests) are simply python unit tests. They can be run via pytest or directly from IDE.

The [integration_tests](integration_tests) are also python tests. They run against intwdf cluster. 
 