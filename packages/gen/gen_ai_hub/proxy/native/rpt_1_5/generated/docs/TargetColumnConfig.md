# TargetColumnConfig

Configuration for a target column in the prediction model.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The name of the target column. | 
**prediction_placeholder** | [**PredictionPlaceholder**](PredictionPlaceholder.md) |  | 
**task_type** | **str** | The type of prediction task for this column. If not provided, the model will infer the task type from the data. | [optional] 
**top_k** | **int** | How many predictions to output for this classification column.If not provided, only a single prediction is returned. Only relevant for classification. | [optional] 

## Example

```python
from rpt_1_5_generated.models.target_column_config import TargetColumnConfig

# TODO update the JSON string below
json = "{}"
# create an instance of TargetColumnConfig from a JSON string
target_column_config_instance = TargetColumnConfig.from_json(json)
# print the JSON string representation of the object
print(TargetColumnConfig.to_json())

# convert the object into a dict
target_column_config_dict = target_column_config_instance.to_dict()
# create an instance of TargetColumnConfig from a dict
target_column_config_from_dict = TargetColumnConfig.from_dict(target_column_config_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


