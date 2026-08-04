# ExplanationResult

Explanation data for predictions.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**top_column_scores** | **List[Dict[str, float]]** | Column scores per query row extracted from the model (higher means more weight was put on this column). | [optional] 
**top_relevant_context_rows** | **List[List[int]]** | 2D array where each subarray contains indices of most relevant context rows for that query row. The first dimension indexes query rows, the second dimension indexes all rows as a sequential integer index. | [optional] 

## Example

```python
from rpt_1_5_generated.models.explanation_result import ExplanationResult

# TODO update the JSON string below
json = "{}"
# create an instance of ExplanationResult from a JSON string
explanation_result_instance = ExplanationResult.from_json(json)
# print the JSON string representation of the object
print(ExplanationResult.to_json())

# convert the object into a dict
explanation_result_dict = explanation_result_instance.to_dict()
# create an instance of ExplanationResult from a dict
explanation_result_from_dict = ExplanationResult.from_dict(explanation_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


