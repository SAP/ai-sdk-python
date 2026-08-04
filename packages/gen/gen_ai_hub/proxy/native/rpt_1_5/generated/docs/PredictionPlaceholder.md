# PredictionPlaceholder

The placeholder value in any column for which to predict a value. The model will predict a value for all table cells containing this value.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------

## Example

```python
from rpt_1_5_generated.models.prediction_placeholder import PredictionPlaceholder

# TODO update the JSON string below
json = "{}"
# create an instance of PredictionPlaceholder from a JSON string
prediction_placeholder_instance = PredictionPlaceholder.from_json(json)
# print the JSON string representation of the object
print(PredictionPlaceholder.to_json())

# convert the object into a dict
prediction_placeholder_dict = prediction_placeholder_instance.to_dict()
# create an instance of PredictionPlaceholder from a dict
prediction_placeholder_from_dict = PredictionPlaceholder.from_dict(prediction_placeholder_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


