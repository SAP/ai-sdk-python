# SAP Cloud SDK for AI (Python): Core SDK
The SDK formerly known as *AI Core SDK* was rebranded.

The class names have not changed i.e., you can continue to use existing code.

The SAP AI Core SDK can be used to interact with SAP AI Core. 
It provides access to all public lifecycle and administration APIs.

For example:

* You can execute pipelines as a batch job to preprocess or train your models, or perform batch inference.

* You can deploy а trained machine learning model as a web service to serve inference requests with high performance.

* You can register your own Docker registry, synchronize your AI content from your own git repository, and register your own object store for training data and trained models.

* You can log metrics within a workflow execution using the SDK. You can use the same code for tracking metrics in both your local environment and in the workflow execution (production).

> **Notes**
>
> - Executing online inference is not part of Core SDK.
>
> - Metrics persistence is not currently available in your local environment using the SDK. However, it is available in your productive workflow execution.
>
> - *Content packages* for AICore are no longer supported.
> 
## Example Usage

Here are a few examples how to use this SDK. 
For details on the methods, please refer to the [API documentation](https://api.sap.com/api/AI_CORE_API/resource/Scenario).

### Import Definitions

```python
from ai_core_sdk.ai_core_v2_client import AICoreV2Client
```

## Create Client

The SDK requires credentials from your tenant's subaccount Service Key:
```python
client = AICoreV2Client(base_url=AI_API_BASE,
                        auth_url=AUTH_URL,
                        client_id=CLIENT_ID,
                        client_secret=CLIENT_SECRET,
                        resource_group=resource_group_id)
```
(For persistent client configuration see below.)

### Create New Resource Group

```python
resource_group_create = client.resource_groups.create(resource_group_id=resource_group_id)
print(resource_group_create.resource_group_id)
resource_group_details = client.resource_groups.get(resource_group_id=resource_group_id)
print(f"{resource_group_details.status_message} \n{resource_group_details.resource_group_id}")
```

### Create Object Store Secret

```python
# access key and secret are assumed to reside in environment variables OSS_KEY and OSS_SECRET
object_store_secret_create = client.object_store_secrets.create(
            name="default",
            type="S3",
            bucket="<your S3 bucket>", 
            endpoint="<your S3 host>",
            path_prefix="<your path prefix in S3>", region="<your S3 region>",
            data={"AWS_ACCESS_KEY_ID": os.environ.get("OSS_KEY"),
            "AWS_SECRET_ACCESS_KEY": os.environ.get("OSS_SECRET")})

secret_get = client.object_store_secrets.get(name="default")
print(f"{secret_get.metadata}")
```

### List Scenarios

```python
scenarios = client.scenario.query()
for scenario in scenarios.resources:
    print(f"{scenario.name} {scenario.id}")
```
## Client Configuration

There are different options to persist the client credentials
(in this order of precedence): 
 - in code via keyword arguments (see above),
 - environment variables,
 - profile configuration file.
 - from VCAP_SERVICES environment variable, if exists

A **profile** is a json file residing in a config directory, 
which can be set via environment variable `AICORE_HOME` (the default being `~/.aicore/config.json`).

The command `aicore configure --help` shows the options for generating a profile.

With profile names one can switch easily between profiles e.g., for different (sub)accounts.
The profile name can be passed also as a keyword. If no profile is specified, the default profile is used.

## Tracking

 The tracking module of the SAP AI Core SDK can be used to log metrics in both your local environment, and productive workflow executions. Metrics persistence is currently available in your productive environment.

 Here are a few code samples demonstrating how to use the SDK for metrics tracking.


### Modify Metrics

 ```
 from ai_core_sdk.tracking import Tracking

 from ai_core_sdk.models import Metric, MetricTag, MetricCustomInfo

 tracking_client = Tracking()

 tracking_client.modify(
    tags = [
        # list
        MetricTag(name="Our Team Tag", value="Tutorial Team"),
        MetricTag(name="Stage", value="Development")
    ],
    metrics = [
        Metric(
            name="Training Loss",
            value=np.finfo(np.float64).max,
            timestamp= datetime.now().utcnow(),
            step = 1, # denotes epoch 1
            labels = []
        )
    ],
    custom_info = [
        # list of Custom Information
         MetricCustomInfo(
             name = "My Classification Report",
             # you may convert anything to string and store it
             value = str('''{
                 "Cats": {
                     "Precision": 75,
                     "Recall": 74
                 },
                 "Dogs": {
                     "Precision": 85,
                     "Recall": 84
                 }
             }''')
        )
    ]
 )

 ```

 ### Log Metrics

 ```
 tracking_client.log_metrics(
    metrics = [
        Metric(
            name="Training Loss",
            value=float(86.99),
            timestamp= datetime.now().utcnow(),
            step = 1, # denotes epoch 1
            labels = []
        ),
    ],
 )

 ```

 ### Set Tags

 ```
 tracking_client.set_tags(
    tags = [
        # list
        MetricTag(name="Our Team Tag", value="Tutorial Team"),
        MetricTag(name="Stage", value="Development")
    ]
 )

 ```

 ### Set Custom Info

 ```
 tracking_client.set_custom_info(
    custom_info = [
        # list of Custom Information
         MetricCustomInfo(
             name = "My Classification Report",
             # you may convert anything to string and store it
             value = str('''
             {
                 "Cats": {
                     "Precision": 75,
                     "Recall": 74
                 },
                 "Dogs": {
                     "Precision": 85,
                     "Recall": 84
                 }
             }
             '''
             )
        ),
    ]
 )

 ```
  ### Query Metrics

 ```
 metrics_response = tracking_client.query(execution_ids = [
    "test_execution_id"    # Change this with the training execution id
 ])
 ```

  ### Delete Metrics

 ```
 metrics_response = tracking_client.delete(execution_id = "test_execution_id") # Change this with the actual execution id
 ```
