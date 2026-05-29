
# SAP Cloud SDK for AI (Python): Base Client for AI API
The SDK formerly known as *AI API Client SDK* was rebranded.

The class names have not changed i.e., you can continue to use existing code.

The Base Client for AI API is a Python-based SDK that enables you to access the AI API using Python methods and data 
structures.

The Base SDK can be used with any implementation of AI API. Because it is independent of the runtime implementation, it doesn't provide access to runtime-specific APIs. For example, maintaining object store secrets is specific to SAP AI Core and is therefore not included in the Base SDK. Check for SDK offerings for your runtime that let you access any runtime-specific APIs. For more information on the Core SDK see <https://pypi.org/project/sap-ai-sdk-core/>.

For more information on the AI API specification, SAP AI Core and related topics, please refer to <https://help.sap.com/docs/AI_CORE?version=CLOUD>.

## Example Usage

```python
from ai_api_client_sdk.ai_api_v2_client import AIAPIV2Client

# Instantiate the client
client = AIAPIV2Client(base_url=AI_API_URL,
    auth_url=AUTH_URL,
    client_id=CLIENT_ID, 
    client_secret=CLIENT_SECRET, resource_group=RESOURCE_GROUP)

# Make some queries, e.g. 
scenarios = client.scenario.query()

for scenario in scenarios.resources:
    print(scenario.id)

# Find a deployable executables in scenario 1111
executables = client.executable.query(scenario_id="1111")
for executable in executables.resources:
    if executable.deployable == False:
        break
print(executable.id)

# Inspect the required parameters for the executable
for parameter in executable.parameters:
    print("Parameter:{}, Type: {}".format(parameter.name, parameter.type))

# Create a configuration
parameter_epochs = ParameterBinding(key="training-epochs", value="1")
myConfiguration = client.configuration.create(name="test", scenario_id="1111" executable_id="argo-mnist-0.2.1", parameter_bindings=[parameter_epochs])
```
