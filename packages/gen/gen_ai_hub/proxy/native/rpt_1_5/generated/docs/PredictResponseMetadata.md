# PredictResponseMetadata

Metadata about the prediction request.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**num_columns** | **int** | Number of columns in the input data. | 
**num_rows** | **int** | Number of rows in the input data. | 
**num_predictions** | **int** | Number of table cells containing the specified placeholder value. | 
**num_query_rows** | **int** | Number of rows for which a prediction was made. | 

## Example

```python
from rpt_1_5_generated.models.predict_response_metadata import PredictResponseMetadata

# TODO update the JSON string below
json = "{}"
# create an instance of PredictResponseMetadata from a JSON string
predict_response_metadata_instance = PredictResponseMetadata.from_json(json)
# print the JSON string representation of the object
print(PredictResponseMetadata.to_json())

# convert the object into a dict
predict_response_metadata_dict = predict_response_metadata_instance.to_dict()
# create an instance of PredictResponseMetadata from a dict
predict_response_metadata_from_dict = PredictResponseMetadata.from_dict(predict_response_metadata_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


