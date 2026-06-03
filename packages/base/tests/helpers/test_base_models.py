from unittest import TestCase

from ai_api_client_sdk.models.base_models import KeyValue, NameValue, Name, QueryResponse, BasicResponse


class TestBaseModels(TestCase):
    def test_key_value_string_representation(self):
        key = "dummy_key"
        value = "dummy_value"
        key_value_object = KeyValue(key=key, value=value)
        self.assertIn("Key: ", key_value_object.__str__())
        self.assertIn(key, key_value_object.__str__())
        self.assertIn("Value: ", key_value_object.__str__())
        self.assertIn(value, key_value_object.__str__())

    def test_name_value_string_representation(self):
        name = "dummy_name"
        value = "dummy_value"
        name_value_object = NameValue(name=name, value=value)
        self.assertIn("Name: ", name_value_object.__str__())
        self.assertIn(name, name_value_object.__str__())
        self.assertIn("Value: ", name_value_object.__str__())
        self.assertIn(value, name_value_object.__str__())

    def test_name_string_representation(self):
        name = "dummy_name"
        name_object = Name(name=name)
        self.assertIn("Name: ", name_object.__str__())
        self.assertIn(name, name_object.__str__())

    def test_query_response_string_representation(self):
        resources = ["dummy_resource1", "dummy_resource2"]
        count = 1
        query_response_object = QueryResponse(resources=resources, count=count)
        self.assertIn("Resources: ", query_response_object.__str__())
        for resource in resources:
            self.assertIn(str(resource), query_response_object.__str__())
        self.assertIn("Count: ", query_response_object.__str__())
        self.assertIn(str(count), query_response_object.__str__())

    def test_basic_response_string_representation(self):
        dummy_id = "dummy_id"
        message = "dummy_message"
        name_object = BasicResponse(id=dummy_id, message=message)
        self.assertIn("Id: ", name_object.__str__())
        self.assertIn(dummy_id, name_object.__str__())
        self.assertIn("Message: ", name_object.__str__())
        self.assertIn(message, name_object.__str__())
