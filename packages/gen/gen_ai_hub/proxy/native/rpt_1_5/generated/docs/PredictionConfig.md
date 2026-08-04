# PredictionConfig

Configuration of the prediction model.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**target_columns** | [**List[TargetColumnConfig]**](TargetColumnConfig.md) |  | 
**explanations** | [**ExplanationConfig**](ExplanationConfig.md) | Optional configuration for explainability outputs (column scores and relevant context rows). | [optional] 

## Example

```python
from rpt_1_5_generated.models.prediction_config import PredictionConfig

# TODO update the JSON string below
json = "{}"
# create an instance of PredictionConfig from a JSON string
prediction_config_instance = PredictionConfig.from_json(json)
# print the JSON string representation of the object
print(PredictionConfig.to_json())

# convert the object into a dict
prediction_config_dict = prediction_config_instance.to_dict()
# create an instance of PredictionConfig from a dict
prediction_config_from_dict = PredictionConfig.from_dict(prediction_config_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


