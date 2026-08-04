# PredictResponsePayload

Response payload for prediction requests. Contains a list of prediction results.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Unique ID for the request. | 
**status** | [**PredictResponseStatus**](PredictResponseStatus.md) | Status message that can indicate warnings (e.g. about suboptimal data). | 
**predictions** | **List[Dict[str, PredictionsInnerValue]]** | Mapping of column names to their list of prediction results or index column. | 
**explanations** | [**ExplanationResult**](ExplanationResult.md) | Explanation data containing context row and column scores. | [optional] 
**metadata** | [**PredictResponseMetadata**](PredictResponseMetadata.md) |  | 

## Example

```python
from rpt_1_5_generated.models.predict_response_payload import PredictResponsePayload

# TODO update the JSON string below
json = "{}"
# create an instance of PredictResponsePayload from a JSON string
predict_response_payload_instance = PredictResponsePayload.from_json(json)
# print the JSON string representation of the object
print(PredictResponsePayload.to_json())

# convert the object into a dict
predict_response_payload_dict = predict_response_payload_instance.to_dict()
# create an instance of PredictResponsePayload from a dict
predict_response_payload_from_dict = PredictResponsePayload.from_dict(predict_response_payload_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


