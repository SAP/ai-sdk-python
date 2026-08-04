# PredictRequestPayloadOneOf1


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**prediction_config** | [**PredictionConfig**](PredictionConfig.md) | Configuration of target columns and placeholder value. | 
**index_column** | **str** | The name of the index column. If provided, the service will return this column&#39;s value in each prediction object to facilitate aligning the output predictions with the input rows on the client side. If not provided, the column will not be included in the output. | [optional] 
**parse_data_types** | **bool** | Whether to parse the data types of the columns. If set to True, numeric columns will be parsed to float or integer and dates in ISO format YYYY-MM-DD will be parsed. | [optional] [default to True]
**data_schema** | [**Dict[str, SchemaFieldConfig]**](SchemaFieldConfig.md) | Optional schema defining the data types of each column. If provided, this will override automatic data type parsing. | [optional] 
**columns** | **Dict[str, List[RowsInnerValue]]** | Alternative to rows: columns of data where each key is a column name and the value is a list of all column values. Either \&quot;rows\&quot; or \&quot;columns\&quot; must be provided. | 

## Example

```python
from rpt_1_5_generated.models.predict_request_payload_one_of1 import PredictRequestPayloadOneOf1

# TODO update the JSON string below
json = "{}"
# create an instance of PredictRequestPayloadOneOf1 from a JSON string
predict_request_payload_one_of1_instance = PredictRequestPayloadOneOf1.from_json(json)
# print the JSON string representation of the object
print(PredictRequestPayloadOneOf1.to_json())

# convert the object into a dict
predict_request_payload_one_of1_dict = predict_request_payload_one_of1_instance.to_dict()
# create an instance of PredictRequestPayloadOneOf1 from a dict
predict_request_payload_one_of1_from_dict = PredictRequestPayloadOneOf1.from_dict(predict_request_payload_one_of1_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


