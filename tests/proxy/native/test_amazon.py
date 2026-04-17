import json
import time
import unittest
from typing import Iterator
from unittest.mock import AsyncMock, MagicMock, patch

from botocore.config import Config
from aiobotocore.config import AioConfig

from gen_ai_hub.proxy.native.amazon.clients import Session, ClientWrapper, AsyncSession, AsyncClientWrapper
from tests.mock import (AMAZON_BEDROCK_RESPONSE,
                        AMAZON_BEDROCK_BROKEN_STREAM_RESPONSE,
                        get_mocked_ai_core_client,
                        )
from tests.proxy.langchain_.test_init_models import TestInitModels


def get_bedrock_messages_inference_config():
    return {"maxTokens": 512, "temperature": 0.5, "topP": 0.9}


def get_bedrock_messages():
    return [
        {
            "role": "user",
            "content": [
                {
                    "text": "Describe the purpose of a 'hello world' program in one line."
                }
            ],
        }
    ]


def get_bedrock_prompt():
    return json.dumps(
        {
            "inputText": "Explain black holes to 8th graders.",
            "textGenerationConfig": {
                "maxTokenCount": 3072,
                "stopSequences": [],
                "temperature": 0.7,
                "topP": 0.9,
            },
        }
    )

def get_delayed_bedrock_response(delay) -> Iterator[bytes]:
    response = AMAZON_BEDROCK_RESPONSE
    for line in response:
        yield line
        time.sleep(delay)  # Simulate delay


class TestAmazonModels(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.proxy_client = get_mocked_ai_core_client()
        cls.proxy_client._get_scenario_deployments = MagicMock()
        cls.http_mock = MagicMock()
        cls.http_mock.status_code = 200
        cls.parsed_response_mock = MagicMock()

    @patch("gen_ai_hub.proxy.native.amazon.clients.BaseClient._make_request")
    def test_completion(self, mock_make_request):
        mock_make_request.return_value = (self.http_mock, self.parsed_response_mock)
        bedrock = Session().client(
            model_name="amazon--nova-premier", proxy_client=self.proxy_client
        )
        response = bedrock.invoke_model(body=get_bedrock_prompt())
        self.assertIsInstance(response, MagicMock)
        mock_make_request.assert_called_once()
        self.assertEqual(mock_make_request.call_args.args[1]["url_path"], "invoke")
        deployment = self.proxy_client.select_deployment(
            model_name="amazon--nova-premier"
        )
        self.assertEqual(
            mock_make_request.call_args.args[1]["url"],
            deployment.url + "/invoke",
        )

    @patch("gen_ai_hub.proxy.native.amazon.clients.BaseClient._make_request")
    def test_completion_with_custom_model(self, mock_make_request):
        mock_make_request.return_value = (self.http_mock, self.parsed_response_mock)
        model_name = 'test-custom-model'
        custom_deployment = TestInitModels.create_deployment(model_name)
        self.proxy_client._deployments.append(custom_deployment)
        bedrock = Session().client(model_name=model_name, proxy_client=self.proxy_client)
        bedrock.invoke_model(body=get_bedrock_prompt())
        mock_make_request.assert_called_once()
        self.assertEqual(mock_make_request.call_args.args[1]["url_path"], "invoke")
        deployment = self.proxy_client.select_deployment(
            model_name=model_name
        )
        self.assertEqual(
            mock_make_request.call_args.args[1]["url"],
            deployment.url + "/invoke",
        )

    @patch("gen_ai_hub.proxy.native.amazon.clients.BaseClient._make_request")
    def test_update_deployments_called_for_custom_model(self, mock_make_request):
        mock_make_request.return_value = (self.http_mock, self.parsed_response_mock)
        model_name = 'test-custom-model-1'
        custom_deployment = TestInitModels.create_deployment(model_name)
        deployments = TestInitModels.create_gen_ai_hub_deployments()
        deployments.append(custom_deployment)
        deployments_dict = {}
        for i in range(len(deployments)):
            deployments_dict[i] = deployments[i]
        self.proxy_client._get_scenario_deployments.return_value = deployments_dict

        bedrock = Session().client(model_name=model_name, proxy_client=self.proxy_client)
        bedrock.invoke_model(body=get_bedrock_prompt())
        mock_make_request.assert_called_once()
        self.assertEqual(mock_make_request.call_args.args[1]["url_path"], "invoke")
        deployment = self.proxy_client.select_deployment(
            model_name=model_name
        )
        self.assertEqual(
            mock_make_request.call_args.args[1]["url"],
            deployment.url + "/invoke",
        )
        self.proxy_client._get_scenario_deployments.assert_called_once_with(
            self.proxy_client.foundational_model_scenarios[0])

    @patch("gen_ai_hub.proxy.native.amazon.clients.BaseClient._make_request")
    def test_completion_streaming(self, mock_make_request):
        mock_make_request.return_value = (self.http_mock, self.parsed_response_mock)
        bedrock = Session().client(
            model_name="amazon--nova-premier", proxy_client=self.proxy_client
        )
        response = bedrock.invoke_model_with_response_stream(body=get_bedrock_prompt())
        self.assertIsInstance(response, MagicMock)
        mock_make_request.assert_called_once()
        self.assertEqual(mock_make_request.call_args.args[1]["url_path"], "invoke-with-response-stream")
        deployment = self.proxy_client.select_deployment(
            model_name="amazon--nova-premier"
        )
        self.assertEqual(
            mock_make_request.call_args.args[1]["url"],
            deployment.url + "/invoke-with-response-stream",
        )

    @patch("gen_ai_hub.proxy.native.amazon.clients.BaseClient._make_request")
    def test_completion_streaming_with_deprecated_timeout(self, mock_make_request):
        mock_make_request.return_value = (self.http_mock, self.parsed_response_mock)
        bedrock = Session().client(
            model_name="amazon--nova-premier", proxy_client=self.proxy_client
        )
        with self.assertWarns(DeprecationWarning):
            response = bedrock.invoke_model_with_response_stream(body=get_bedrock_prompt(), timeout=120)
            self.assertIsInstance(response, MagicMock)
            mock_make_request.assert_called_once()
            self.assertEqual(mock_make_request.call_args.args[1]["url_path"], "invoke-with-response-stream")
            deployment = self.proxy_client.select_deployment(
                model_name="amazon--nova-premier"
            )
            self.assertEqual(
                mock_make_request.call_args.args[1]["url"],
                deployment.url + "/invoke-with-response-stream",
            )


    @patch("gen_ai_hub.proxy.native.amazon.clients.BaseClient._make_request")
    def test_completion_stream_chunks(self, mock_make_request):
        mock_make_request.return_value = (self.http_mock, self.parsed_response_mock)
        bedrock = Session().client(
            model_name="amazon--nova-premier", proxy_client=self.proxy_client
        )
        response = bedrock.invoke_model_with_response_stream(
            body=get_bedrock_prompt()
        )

        stream = response["body"]
        self.assertTrue(all(isinstance(json.loads(event["chunk"]["bytes"])["type"], str) for event in stream))

    @patch("gen_ai_hub.proxy.native.amazon.clients.BaseClient._make_request")
    def test_broken_stream_chunks(self, mock_make_request):
        mock_make_request.return_value = (self.http_mock, AMAZON_BEDROCK_BROKEN_STREAM_RESPONSE)
        bedrock = Session().client(
            model_name="amazon--nova-premier", proxy_client=self.proxy_client
        )
        response = bedrock.invoke_model_with_response_stream(
            body=get_bedrock_prompt()
        )

        with self.assertRaises(ValueError):
            for event in response['body']:
                json.loads(event["chunk"]["bytes"])

    @patch("gen_ai_hub.proxy.native.amazon.clients.BaseClient._make_request")
    def test_stream_is_not_buffered(self, mock_make_request):
        delay = 1
        self.http_mock.iter_lines.return_value = (
            get_delayed_bedrock_response(1)
        )
        mock_make_request.return_value = (self.http_mock, self.parsed_response_mock)
        bedrock = Session().client(
            model_name="amazon--nova-premier", proxy_client=self.proxy_client
        )
        response = bedrock.invoke_model_with_response_stream(
            body=get_bedrock_prompt()
        )

        stream = response["body"]
        times = []
        for event in stream:
            times.append(time.time())
            self.assertIsInstance(json.loads(event["chunk"]["bytes"])["type"], str)
        for i in range(1, len(times)):
            self.assertGreaterEqual(times[i] - times[i - 1], delay - 0.25)

    @patch("gen_ai_hub.proxy.native.amazon.clients.BaseClient._make_request")
    def test_chat_completion(self, mock_make_request):
        mock_make_request.return_value = (self.http_mock, self.parsed_response_mock)
        bedrock = Session().client(
            model_name="amazon--nova-premier", proxy_client=self.proxy_client
        )
        response = bedrock.converse(
            messages=get_bedrock_messages(),
            inferenceConfig=get_bedrock_messages_inference_config(),
        )
        self.assertIsInstance(response, MagicMock)
        mock_make_request.assert_called_once()
        self.assertEqual(mock_make_request.call_args.args[1]["url_path"], "converse")
        deployment = self.proxy_client.select_deployment(
            model_name="amazon--nova-premier"
        )
        self.assertEqual(
            mock_make_request.call_args.args[1]["url"],
            deployment.url + "/converse",
        )

    @patch("gen_ai_hub.proxy.native.amazon.clients.BaseClient._make_request")
    def test_chat_converse_streaming(self, mock_make_request):
        mock_make_request.return_value = (self.http_mock, self.parsed_response_mock)
        bedrock = Session().client(
            model_name="amazon--nova-premier", proxy_client=self.proxy_client
        )
        response = bedrock.converse_stream(
            messages=get_bedrock_messages(),
            inferenceConfig=get_bedrock_messages_inference_config(),
        )
        self.assertIsInstance(response, MagicMock)
        mock_make_request.assert_called_once()
        self.assertEqual(mock_make_request.call_args.args[1]["url_path"], "converse-stream")
        deployment = self.proxy_client.select_deployment(
            model_name="amazon--nova-premier"
        )
        self.assertEqual(
            mock_make_request.call_args.args[1]["url"],
            deployment.url + "/converse-stream",
        )

    def test_config_parameters(self):
        custom_config = Config({'temperature': 0})
        self.assertIsInstance(
            Session().client(model_name="amazon--nova-premier",
                             proxy_client=self.proxy_client,
                             region_name='us', config=custom_config),
            ClientWrapper
        )

    def test_service_name(self):
        with self.assertRaises(NotImplementedError):
            Session().client(model_name="amazon--nova-premier",
                             proxy_client=self.proxy_client,
                             service_name="Claude")


class TestAsyncClientWrapper(unittest.IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.proxy_client = get_mocked_ai_core_client()
        cls.proxy_client._get_scenario_deployments = MagicMock()
        cls.http_mock = MagicMock()
        cls.http_mock.status_code = 200
        cls.parsed_response_mock = MagicMock()

    async def test_config_parameters_for_async(self):
        custom_config = AioConfig(
            read_timeout=120,
            connect_timeout=120,
        )
        res_client = await AsyncSession().async_client(model_name="amazon--nova-premier",
                                                 proxy_client=self.proxy_client,
                                                 region_name='us', config=custom_config)
        self.assertIsInstance(
            res_client,
            AsyncClientWrapper
        )
        self.assertEqual(res_client._client_config.read_timeout, 120)
        self.assertEqual(res_client._client_config.connect_timeout, 120)

    async def test_async_client(self):
        with self.assertRaises(NotImplementedError):
            await AsyncSession().async_client(model_name="amazon--nova-premier",
                                        proxy_client=self.proxy_client,
                                        service_name="Claude")

    @patch("gen_ai_hub.proxy.native.amazon.clients.AioBaseClient._make_request")
    async def test_async_invoke_model(self, mock_make_request):
        mock_make_request.return_value = (self.http_mock, self.parsed_response_mock)
        bedrock = await AsyncSession().async_client(
            model_name="amazon--nova-premier", proxy_client=self.proxy_client
        )
        response = await bedrock.invoke_model(body=get_bedrock_prompt())
        self.assertIsInstance(response, MagicMock)
        mock_make_request.assert_called_once()
        self.assertEqual(mock_make_request.call_args.args[1]["url_path"], "invoke")
        deployment = self.proxy_client.select_deployment(
            model_name="amazon--nova-premier"
        )
        self.assertEqual(
            mock_make_request.call_args.args[1]["url"],
            deployment.url + "/invoke",
        )

    @patch("gen_ai_hub.proxy.native.amazon.clients.AioBaseClient._make_request")
    async def test_async_converse(self, mock_make_request):
        mock_make_request.return_value = (self.http_mock, self.parsed_response_mock)
        bedrock = await AsyncSession().async_client(
            model_name="amazon--nova-premier", proxy_client=self.proxy_client
        )
        response = await bedrock.converse(
            messages=get_bedrock_messages(),
            inferenceConfig=get_bedrock_messages_inference_config(),
        )
        self.assertIsInstance(response, MagicMock)
        mock_make_request.assert_called_once()
        self.assertEqual(mock_make_request.call_args.args[1]["url_path"], "converse")
        deployment = self.proxy_client.select_deployment(
            model_name="amazon--nova-premier"
        )
        self.assertEqual(
            mock_make_request.call_args.args[1]["url"],
            deployment.url + "/converse",
        )

    @patch("gen_ai_hub.proxy.native.amazon.clients.AioBaseClient._make_request")
    async def test_async_converse_streaming(self, mock_make_request):
        mock_make_request.return_value = (self.http_mock, self.parsed_response_mock)
        bedrock = await AsyncSession().async_client(
            model_name="amazon--nova-premier", proxy_client=self.proxy_client
        )
        response = await bedrock.converse_stream(
            messages=get_bedrock_messages(),
            inferenceConfig=get_bedrock_messages_inference_config(),
        )
        self.assertIsInstance(response, MagicMock)
        mock_make_request.assert_called_once()
        self.assertEqual(mock_make_request.call_args.args[1]["url_path"], "converse-stream")
        deployment = self.proxy_client.select_deployment(
            model_name="amazon--nova-premier"
        )
        self.assertEqual(
            mock_make_request.call_args.args[1]["url"],
            deployment.url + "/converse-stream",
        )


    @patch("gen_ai_hub.proxy.native.amazon.clients.AioBaseClient._make_request")
    async def test_async_invoke_streaming(self, mock_make_request):
        mock_make_request.return_value = (self.http_mock, self.parsed_response_mock)

        bedrock = await AsyncSession().async_client(
            model_name="amazon--nova-premier", proxy_client=self.proxy_client
        )
        response = await bedrock.invoke_model_with_response_stream(body=get_bedrock_prompt())
        self.assertIsInstance(response, MagicMock)
        mock_make_request.assert_called_once()
        self.assertEqual(mock_make_request.call_args.args[1]["url_path"], "invoke-with-response-stream")
        deployment = self.proxy_client.select_deployment(
            model_name="amazon--nova-premier"
        )
        self.assertEqual(
            mock_make_request.call_args.args[1]["url"],
            deployment.url + "/invoke-with-response-stream",
        )

    @patch("gen_ai_hub.proxy.native.amazon.clients.AioBaseClient._make_request")
    async def test_async_invoke_streaming_reads_response_on_error(self, mock_make_request):
        mock_make_request.side_effect = Exception("Error")

        bedrock = await AsyncSession().async_client(
            model_name="amazon--nova-premier", proxy_client=self.proxy_client
        )
        with self.assertRaises(Exception) as context:
            await bedrock.invoke_model_with_response_stream(body=get_bedrock_prompt())

        self.assertEqual(str(context.exception), "Error")

        mock_make_request.assert_called_once()
        deployment = self.proxy_client.select_deployment(
            model_name="amazon--nova-premier"
        )

        self.assertEqual(
            mock_make_request.call_args.args[1]["url"],
            deployment.url + "/invoke-with-response-stream",
        )

    async def test_cleanup_handles_exceptions_gracefully(self):
        """Test that _cleanup() handles exceptions without raising."""
        # Create a real client first
        bedrock = await AsyncSession().async_client(
            model_name="amazon--nova-premier",
            proxy_client=self.proxy_client
        )

        # Replace the context manager with a mock that raises on __aexit__
        mock_context_manager = MagicMock()
        mock_aexit = AsyncMock(side_effect=Exception("Cleanup error"))
        mock_context_manager.__aexit__ = mock_aexit
        bedrock._context_manager = mock_context_manager

        # Call cleanup and verify it doesn't raise
        try:
            await bedrock._close()
            cleanup_succeeded = True
        except Exception:
            cleanup_succeeded = False

        self.assertTrue(cleanup_succeeded, "_cleanup() should handle exceptions gracefully")
        # Verify __aexit__ was called despite the exception
        mock_aexit.assert_called_once_with(None, None, None)
        # Verify context manager was set to None
        self.assertIsNone(bedrock._context_manager)

    async def test_close_calls_cleanup(self):
        """Test that close() properly calls _cleanup()."""
        bedrock = await AsyncSession().async_client(
            model_name="amazon--nova-premier",
            proxy_client=self.proxy_client
        )

        # Replace context manager with a mock to track calls
        mock_context_manager = MagicMock()
        mock_aexit = AsyncMock()
        mock_context_manager.__aexit__ = mock_aexit
        bedrock._context_manager = mock_context_manager

        # Call close explicitly
        await bedrock.close()

        # Verify __aexit__ was called
        mock_aexit.assert_called_once_with(None, None, None)
        # Verify context manager was set to None
        self.assertIsNone(bedrock._context_manager)

    async def test_context_manager_cleanup(self):
        """Test that using async with properly cleans up."""
        # Create client and replace context manager with mock
        bedrock = await AsyncSession().async_client(
            model_name="amazon--nova-premier",
            proxy_client=self.proxy_client
        )

        mock_context_manager = MagicMock()
        mock_aexit = AsyncMock()
        mock_context_manager.__aexit__ = mock_aexit
        original_context_manager = bedrock._context_manager
        bedrock._context_manager = mock_context_manager

        # Use async with context manager
        async with bedrock:
            # Client is usable inside context
            self.assertIsInstance(bedrock, AsyncClientWrapper)

        # Verify __aexit__ was called after context exit
        mock_aexit.assert_called_once_with(None, None, None)
        # Verify context manager was set to None
        self.assertIsNone(bedrock._context_manager)

        # Clean up the original context manager
        await original_context_manager.__aexit__(None, None, None)

def test_flat_import_amazon():
    from gen_ai_hub.proxy.native.amazon import ClientWrapper as client_wrapper_flat_import
    from gen_ai_hub.proxy.native.amazon.clients import ClientWrapper as client_wrapper_nested_import
    assert client_wrapper_flat_import == client_wrapper_nested_import