# rpt_1_5_generated.DefaultApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**health**](DefaultApi.md#health) | **GET** /health | Health Check
[**predict**](DefaultApi.md#predict) | **POST** /predict | Make predictions from JSON (optionally gzip-compressed).
[**predict_parquet**](DefaultApi.md#predict_parquet) | **POST** /predict_parquet | Make predictions from Parquet file


# **health**
> object health()

Health Check

### Example


```python
import rpt_1_5_generated
from rpt_1_5_generated.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = rpt_1_5_generated.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with rpt_1_5_generated.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = rpt_1_5_generated.DefaultApi(api_client)

    try:
        # Health Check
        api_response = await api_instance.health()
        print("The response of DefaultApi->health:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->health: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **predict**
> PredictResponsePayload predict(predict_request_payload, content_encoding=content_encoding)

Make predictions from JSON (optionally gzip-compressed).

### Example


```python
import rpt_1_5_generated
from rpt_1_5_generated.models.predict_request_payload import PredictRequestPayload
from rpt_1_5_generated.models.predict_response_payload import PredictResponsePayload
from rpt_1_5_generated.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = rpt_1_5_generated.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with rpt_1_5_generated.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = rpt_1_5_generated.DefaultApi(api_client)
    predict_request_payload = {"index_column":"id","prediction_config":{"target_columns":[{"name":"category","prediction_placeholder":"?","task_type":"classification","top_k":1}]},"columns":{"id":[1,2,3,4],"product":["Laptop","Mouse","Keyboard","Monitor"],"price":[899,25,75,350],"category":["Electronics","Accessories","Accessories","?"],"stock":["150","500","320","200"]},"data_schema":{"id":{"dtype":"numeric"},"product":{"dtype":"string"},"price":{"dtype":"numeric"},"category":{"dtype":"string"},"stock":{"dtype":"numeric"}}} # PredictRequestPayload | 
    content_encoding = 'content_encoding_example' # str | Content encoding of the request body. Use 'gzip' for gzip-compressed payloads. Use compression level 1. (optional)

    try:
        # Make predictions from JSON (optionally gzip-compressed).
        api_response = await api_instance.predict(predict_request_payload, content_encoding=content_encoding)
        print("The response of DefaultApi->predict:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->predict: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **predict_request_payload** | [**PredictRequestPayload**](PredictRequestPayload.md)|  | 
 **content_encoding** | **str**| Content encoding of the request body. Use &#39;gzip&#39; for gzip-compressed payloads. Use compression level 1. | [optional] 

### Return type

[**PredictResponsePayload**](PredictResponsePayload.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Prediction |  -  |
**400** | Bad Request - Invalid input data |  -  |
**413** | Payload Too Large |  -  |
**422** | Validation Error |  -  |
**500** | Internal Server Error |  -  |
**503** | Service Unavailable |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **predict_parquet**
> PredictResponsePayload predict_parquet(file, prediction_config, index_column=index_column, parse_data_types=parse_data_types)

Make predictions from Parquet file

### Example


```python
import rpt_1_5_generated
from rpt_1_5_generated.models.predict_response_payload import PredictResponsePayload
from rpt_1_5_generated.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = rpt_1_5_generated.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with rpt_1_5_generated.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = rpt_1_5_generated.DefaultApi(api_client)
    file = 'file_example' # str | 
    prediction_config = 'prediction_config_example' # str | JSON string containing the prediction configuration (see PredictionConfig schema).
    index_column = 'index_column_example' # str |  (optional)
    parse_data_types = False # bool |  (optional) (default to False)

    try:
        # Make predictions from Parquet file
        api_response = await api_instance.predict_parquet(file, prediction_config, index_column=index_column, parse_data_types=parse_data_types)
        print("The response of DefaultApi->predict_parquet:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->predict_parquet: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file** | **str**|  | 
 **prediction_config** | **str**| JSON string containing the prediction configuration (see PredictionConfig schema). | 
 **index_column** | **str**|  | [optional] 
 **parse_data_types** | **bool**|  | [optional] [default to False]

### Return type

[**PredictResponsePayload**](PredictResponsePayload.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Prediction |  -  |
**400** | Bad Request - Invalid input data |  -  |
**413** | Payload Too Large |  -  |
**422** | Validation Error |  -  |
**500** | Internal Server Error |  -  |
**503** | Service Unavailable |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

