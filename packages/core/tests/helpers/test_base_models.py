from unittest import TestCase

from ai_core_sdk.models.base_models import BasicNameResponse, Message


class TestBaseModels(TestCase):
    def test_basic_name_response_string_representation(self):
        name = "dummy_name"
        message = "dummy_message"
        basic_name_response_object = BasicNameResponse(name=name, message=message)
        self.assertIn("Name: ", basic_name_response_object.__str__())
        self.assertIn(name, basic_name_response_object.__str__())
        self.assertIn("Message: ", basic_name_response_object.__str__())
        self.assertIn(message, basic_name_response_object.__str__())

    def test_message_string_representation(self):
        message = "dummy_message"
        message_object = Message(message=message)
        self.assertIn("Message: ", message_object.__str__())
        self.assertIn(message, message_object.__str__())