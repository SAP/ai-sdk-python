# SchemaFieldConfig

Configuration for a single field in the input data schema.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**dtype** | [**ColumnType**](ColumnType.md) | The data type of the column. Supports base types (string, numeric, date) and extended types (e.g., Boolean, Integer, Timestamp). Extended types are mapped to corresponding base types internally. Case-insensitive. | 

## Example

```python
from rpt_1_5_generated.models.schema_field_config import SchemaFieldConfig

# TODO update the JSON string below
json = "{}"
# create an instance of SchemaFieldConfig from a JSON string
schema_field_config_instance = SchemaFieldConfig.from_json(json)
# print the JSON string representation of the object
print(SchemaFieldConfig.to_json())

# convert the object into a dict
schema_field_config_dict = schema_field_config_instance.to_dict()
# create an instance of SchemaFieldConfig from a dict
schema_field_config_from_dict = SchemaFieldConfig.from_dict(schema_field_config_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


