# ExplanationConfig

Configuration for explainability outputs.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**top_column_scores** | **int** | For how many columns to output column scores (optional, default is 0). 0 by default (no explainability). Max value is 20. | [optional] [default to 0]
**top_relevant_context_rows** | **int** | For how many context rows to return indices per query row (optional, default is 0). 0 by default (no explainability). Max value is 20. | [optional] [default to 0]

## Example

```python
from rpt_1_5_generated.models.explanation_config import ExplanationConfig

# TODO update the JSON string below
json = "{}"
# create an instance of ExplanationConfig from a JSON string
explanation_config_instance = ExplanationConfig.from_json(json)
# print the JSON string representation of the object
print(ExplanationConfig.to_json())

# convert the object into a dict
explanation_config_dict = explanation_config_instance.to_dict()
# create an instance of ExplanationConfig from a dict
explanation_config_from_dict = ExplanationConfig.from_dict(explanation_config_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


