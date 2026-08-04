# PredictionResult

A single prediction result for a single column in a single row.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**prediction** | [**Prediction**](Prediction.md) |  | 
**confidence** | **float** | The confidence of the prediction (null for regression predictions). | [optional] 
**confidence_interval** | **List[object]** | Lower and upper bounds of the prediction confidence interval (null for classification predictions). | [optional] 

## Example

```python
from rpt_1_5_generated.models.prediction_result import PredictionResult

# TODO update the JSON string below
json = "{}"
# create an instance of PredictionResult from a JSON string
prediction_result_instance = PredictionResult.from_json(json)
# print the JSON string representation of the object
print(PredictionResult.to_json())

# convert the object into a dict
prediction_result_dict = prediction_result_instance.to_dict()
# create an instance of PredictionResult from a dict
prediction_result_from_dict = PredictionResult.from_dict(prediction_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


