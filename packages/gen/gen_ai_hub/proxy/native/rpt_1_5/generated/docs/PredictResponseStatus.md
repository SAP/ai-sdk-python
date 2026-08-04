# PredictResponseStatus

Output status for prediction requests.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | **int** | Status code (zero means success, other status codes indicate warnings or errors) | 
**message** | **str** | Status message, either \&quot;ok\&quot; or contains a warning / more information. | 

## Example

```python
from rpt_1_5_generated.models.predict_response_status import PredictResponseStatus

# TODO update the JSON string below
json = "{}"
# create an instance of PredictResponseStatus from a JSON string
predict_response_status_instance = PredictResponseStatus.from_json(json)
# print the JSON string representation of the object
print(PredictResponseStatus.to_json())

# convert the object into a dict
predict_response_status_dict = predict_response_status_instance.to_dict()
# create an instance of PredictResponseStatus from a dict
predict_response_status_from_dict = PredictResponseStatus.from_dict(predict_response_status_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


