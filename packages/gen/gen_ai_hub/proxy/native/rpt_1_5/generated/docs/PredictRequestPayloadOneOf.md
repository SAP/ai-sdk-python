# PredictRequestPayloadOneOf


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**prediction_config** | [**PredictionConfig**](PredictionConfig.md) | Configuration of target columns and placeholder value. | 
**index_column** | **str** | The name of the index column. If provided, the service will return this column&#39;s value in each prediction object to facilitate aligning the output predictions with the input rows on the client side. If not provided, the column will not be included in the output. | [optional] 
**parse_data_types** | **bool** | Whether to parse the data types of the columns. If set to True, numeric columns will be parsed to float or integer and dates in ISO format YYYY-MM-DD will be parsed. | [optional] [default to True]
**data_schema** | [**Dict[str, SchemaFieldConfig]**](SchemaFieldConfig.md) | Optional schema defining the data types of each column. If provided, this will override automatic data type parsing. | [optional] 
**rows** | **List[Dict[str, RowsInnerValue]]** | Table rows, i.e. list of objects where each object is a mapping of column names to values. Either \&quot;rows\&quot; or \&quot;columns\&quot; must be provided. | 

## Example

```python
from rpt_1_5_generated.models.predict_request_payload_one_of import PredictRequestPayloadOneOf

# TODO update the JSON string below
json = "{}"
# create an instance of PredictRequestPayloadOneOf from a JSON string
predict_request_payload_one_of_instance = PredictRequestPayloadOneOf.from_json(json)
# print the JSON string representation of the object
print(PredictRequestPayloadOneOf.to_json())

# convert the object into a dict
predict_request_payload_one_of_dict = predict_request_payload_one_of_instance.to_dict()
# create an instance of PredictRequestPayloadOneOf from a dict
predict_request_payload_one_of_from_dict = PredictRequestPayloadOneOf.from_dict(predict_request_payload_one_of_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


