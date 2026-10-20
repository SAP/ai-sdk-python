import json
import unittest

import pytest
from parameterized import parameterized

from gen_ai_hub.proxy.native.amazon.clients import AsyncSession
from gen_ai_hub.proxy.native.amazon.clients import Session
from integration_tests.constants import (AMAZON_NOVA_MICRO_TEST_MODEL, AMAZON_NOVA_PREMIER_TEST_MODEL,
                                         AMAZON_TITAN_EMBEDDING_TEST_MODEL, CLAUDE_4_5_SONNET_TEST_MODEL,
                                         CLAUDE_4_5_HAIKU_TEST_MODEL)
from integration_tests.setup_aicore import TestCaseBedrockSetupMixin


@pytest.mark.bedrock
class AmazonAITests(TestCaseBedrockSetupMixin, unittest.TestCase):
    """
    Titan models were retired and replaced by (multimodal) nova models.
    Documentation on nova models: https://docs.aws.amazon.com/nova/latest/userguide/what-is-nova.html]
    https://docs.aws.amazon.com/bedrock/latest/userguide/inference-methods.html
    """
    def test_client_discovery(self):
        amazon_deployments = [
            deployment
            for deployment in self.proxy_client.deployments
            if any(
                element in deployment.model_name
                for element in [
                    AMAZON_TITAN_EMBEDDING_TEST_MODEL,
                    AMAZON_NOVA_PREMIER_TEST_MODEL,
                    CLAUDE_4_5_SONNET_TEST_MODEL,
                ]
            )
        ]
        self.assertGreater(
            len(amazon_deployments), 0, "No amazon virtual deployments found"
        )

    def test_bedrock_invoke_model(self, model=CLAUDE_4_5_SONNET_TEST_MODEL):
        with self.subTest(model=model):
            bedrock = Session().client(model_name=model)

            body = json.dumps(
                {
                    "max_tokens": 512,
                    "messages": [
                        {
                            "role": "user",
                            "content": "Describe the purpose of a 'hello world' program in one line.",
                        }
                    ],
                    "anthropic_version": "bedrock-2023-05-31",
                    "temperature": 0.0
                }
            )

            response = bedrock.invoke_model(
                body=body,
            )

            response_body = json.loads(response.get("body").read())
            self.assertIsInstance(response, dict)
            self.assertEqual(response["ResponseMetadata"]["HTTPStatusCode"], 200)
            self.assertIsInstance(response_body["content"][0]["text"], str)

    def test_bedrock_invoke_model_with_version(self, model=CLAUDE_4_5_SONNET_TEST_MODEL):
        with self.subTest(model=model):
            bedrock = Session().client(model_name=model, model_version="latest")

            body = json.dumps(
                {
                    "max_tokens": 512,
                    "messages": [
                        {
                            "role": "user",
                            "content": "Describe the purpose of a 'hello world' program in one line.",
                        }
                    ],
                    "anthropic_version": "bedrock-2023-05-31",
                    "temperature": 0.0
                }
            )

            response = bedrock.invoke_model(
                body=body,
            )

            response_body = json.loads(response.get("body").read())
            self.assertIsInstance(response, dict)
            self.assertEqual(response["ResponseMetadata"]["HTTPStatusCode"], 200)
            self.assertIsInstance(response_body["content"][0]["text"], str)

    def test_bedrock_invoke_model_with_response_stream(self, model=CLAUDE_4_5_SONNET_TEST_MODEL):
        with self.subTest(model=model):
            bedrock = Session().client(model_name=model)

            body = json.dumps(
                {
                    "max_tokens": 512,
                    "messages": [
                        {
                            "role": "user",
                            "content": "You are a story teller. Tell me a story about cats.",
                        }
                    ],
                    "anthropic_version": "bedrock-2023-05-31",
                    "temperature": 0.0
                }
            )
            response = bedrock.invoke_model_with_response_stream(
                body=body
            )

            number_of_chunks = 0
            for event in response["body"]:
                chunk = json.loads(event["chunk"]["bytes"])
                if chunk["type"] == "content_block_delta":
                    self.assertIsInstance(chunk["delta"].get("text", ""), str)
                    number_of_chunks += 1
            self.assertGreater(number_of_chunks, 1, "Only one chunk received - stream seems to be buffered.")
            last_chunk = chunk
            self.assertEqual(last_chunk["type"], "message_stop")
            self.assertIn("amazon-bedrock-invocationMetrics", last_chunk)
            metrics = last_chunk["amazon-bedrock-invocationMetrics"]
            self.assertIsInstance(metrics, dict)
            self.assertIn("inputTokenCount", metrics)
            self.assertGreater(metrics["inputTokenCount"], 0)
            self.assertIn("outputTokenCount", metrics)
            self.assertGreater(metrics["outputTokenCount"], 0)

    @parameterized.expand(
        [
            CLAUDE_4_5_SONNET_TEST_MODEL,
            CLAUDE_4_5_HAIKU_TEST_MODEL,
            AMAZON_NOVA_PREMIER_TEST_MODEL,
        ]
    )
    def test_amazon_bedrock_converse(self, model=CLAUDE_4_5_SONNET_TEST_MODEL):
        with self.subTest(model=model):
            bedrock = Session().client(model_name=model)
            conversation = [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": "Describe the purpose of a 'hello world' program in one line."
                        }
                    ],
                }
            ]
            response = bedrock.converse(
                messages=conversation,
                inferenceConfig={"maxTokens": 512, "temperature": 0.0},
            )
            self.assertIsInstance(response, dict)
            self.assertEqual(response["ResponseMetadata"]["HTTPStatusCode"], 200)
            self.assertIsInstance(response["output"]["message"]["content"][0]["text"], str)

    def test_amazon_bedrock_converse_with_tool(self, model=CLAUDE_4_5_SONNET_TEST_MODEL):
        with self.subTest(model=model):
            bedrock = Session().client(model_name=model)
            conversation = [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": "Create a person named Jenny who is 24 years old."
                        }
                    ],
                }
            ]
            tool_config = {
                "tools": [
                    {
                        "toolSpec": {
                            "name": "create_person",
                            "description": "Create a person with name and age.",
                            "inputSchema": {
                                "json": {
                                    "type": "object",
                                    "properties": {
                                        "name": {
                                            "type": "string",
                                            "description": "The name of the person."
                                        },
                                        "age": {
                                            "type": "integer",
                                            "description": "The age of the person."
                                        }
                                    },
                                    "required": ["name", "age"]
                                }
                            }
                        }
                    }
                ]
            }

            response = bedrock.converse(
                messages=conversation,
                toolConfig=tool_config,
                inferenceConfig={"maxTokens": 512, "temperature": 0.0},
            )
            self.assertIsInstance(response, dict)
            self.assertEqual(response["ResponseMetadata"]["HTTPStatusCode"], 200)

            output_message = response["output"]["message"]
            self.assertEqual(output_message["role"], "assistant")

            content = output_message["content"]
            tool_use_block = None
            for c in content:
                if "toolUse" in c:
                    tool_use_block = c["toolUse"]
                    break

            self.assertIsNotNone(tool_use_block, "No tool use block in response")
            self.assertEqual(tool_use_block["name"], "create_person")

            tool_input = tool_use_block["input"]
            self.assertIsInstance(tool_input, dict)
            self.assertEqual(tool_input.get("name"), "Jenny")
            self.assertEqual(tool_input.get("age"), 24)

    @parameterized.expand(
        [
            AMAZON_NOVA_MICRO_TEST_MODEL,
            CLAUDE_4_5_SONNET_TEST_MODEL,
            CLAUDE_4_5_HAIKU_TEST_MODEL,
        ]
    )
    def test_amazon_bedrock_converse_stream(self, model=AMAZON_NOVA_MICRO_TEST_MODEL):
        with self.subTest(model=model):
            bedrock = Session().client(model_name=model)
            conversation = [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": "List all planets in our solar system and give some details about the density, "
                                    "temperature and gravity of each planet."
                        }
                    ],
                }
            ]

            response = bedrock.converse_stream(
                messages=conversation,
                inferenceConfig={"maxTokens": 4090, "temperature": 0.0}
            )

            stream = response['stream']
            response_metadata = response['ResponseMetadata']
            self.assertIsInstance(response_metadata, dict)
            self.assertIn('HTTPHeaders', response_metadata)
            self.assertIsInstance(response_metadata['HTTPHeaders'], dict)
            headers = response_metadata['HTTPHeaders']
            self.assertIn('content-type', headers)
            self.assertEqual(headers['content-type'], 'application/vnd.amazon.eventstream')
            number_of_chunks = 0
            last_three_chunks = []
            for chunk in stream:
                number_of_chunks += 1
                if number_of_chunks == 1:
                    self.assertIn('messageStart', chunk)
                if 'contentBlockDelta' in chunk:
                    delta = chunk['contentBlockDelta']
                    self.assertIsInstance(delta, dict)
                    if 'text' in delta:
                        text = delta['text']
                        self.assertIsInstance(text, str)
                last_three_chunks.append(chunk)
                if len(last_three_chunks) > 3:
                    last_three_chunks.pop(0)
            content_block_stop = last_three_chunks[0]
            self.assertIn('contentBlockStop', content_block_stop)
            message_stop = last_three_chunks[1]
            self.assertIn('messageStop', message_stop)
            metadata = last_three_chunks[2]
            self.assertIn('metadata', metadata)
            metadata = metadata['metadata']
            self.assertIsInstance(metadata, dict)
            self.assertIn('usage', metadata)
            usage = metadata['usage']
            self.assertIsInstance(usage, dict)
            self.assertIn('inputTokens', usage)
            self.assertIn('outputTokens', usage)
            self.assertIn('totalTokens', usage)


    def test_amazon_titan_embedding(self):
        bedrock = Session().client(model_name=AMAZON_TITAN_EMBEDDING_TEST_MODEL)
        body = json.dumps(
            {
                "inputText": "Please recommend books with a theme similar to the movie 'Inception'.",
            }
        )
        response = bedrock.invoke_model(
            body=body,
        )
        response_body = json.loads(response.get("body").read())
        self.assertIsInstance(response, dict)
        self.assertEqual(response["ResponseMetadata"]["HTTPStatusCode"], 200)
        self.assertIsInstance(response_body["embedding"], list)
        self.assertTrue(
            all(isinstance(item, float) for item in response_body["embedding"])
        )


@pytest.mark.bedrock
class AsyncAmazonAITests(TestCaseBedrockSetupMixin, unittest.IsolatedAsyncioTestCase):

    async def test_async_bedrock_invoke_model(self, model=CLAUDE_4_5_SONNET_TEST_MODEL):
        session = AsyncSession()
        bedrock = await session.async_client(model_name=model)
        body = json.dumps(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "Describe the purpose of a 'hello world' program in one line.",
                    }
                ],
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 512,
                "temperature": 0.0
            }
        )

        response = await bedrock.invoke_model(
            body=body,
        )
        response_body = json.loads(await response.get("body").read())
        self.assertIsInstance(response, dict)
        self.assertEqual(response["ResponseMetadata"]["HTTPStatusCode"], 200)
        self.assertIsInstance(response_body["content"][0]["text"], str)

    async def test_async_bedrock_invoke_model_with_model_version(self):
        session = AsyncSession()
        bedrock = await session.async_client(model_name=CLAUDE_4_5_SONNET_TEST_MODEL, model_version="latest")
        body = json.dumps(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "Describe the purpose of a 'hello world' program in one line.",
                    }
                ],
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 512,
                "temperature": 0.0
            }
        )

        response = await bedrock.invoke_model(
            body=body,
        )
        response_body = json.loads(await response.get("body").read())
        self.assertIsInstance(response, dict)
        self.assertEqual(response["ResponseMetadata"]["HTTPStatusCode"], 200)
        self.assertIsInstance(response_body["content"][0]["text"], str)

    async def test_async_bedrock_invoke_with_stream(self):
        session = AsyncSession()
        bedrock = await session.async_client(model_name=CLAUDE_4_5_SONNET_TEST_MODEL)

        body = json.dumps(
            {
                "max_tokens": 512,
                "messages": [
                    {
                        "role": "user",
                        "content": "You are a story teller. Tell me a story about cats.",
                    }
                ],
                "anthropic_version": "bedrock-2023-05-31",
                "temperature": 0.0
            }
        )

        response = await bedrock.invoke_model_with_response_stream(body=body)
        number_of_chunks = 0
        async for event in response["body"]:
            chunk = json.loads(event["chunk"]["bytes"])
            if chunk["type"] == "content_block_delta":
                self.assertIsInstance(chunk["delta"].get("text", ""), str)
                number_of_chunks += 1
        self.assertGreater(number_of_chunks, 1, "Only one chunk received - stream seems to be buffered.")
        last_chunk = chunk
        self.assertEqual(last_chunk["type"], "message_stop")
        self.assertIn("amazon-bedrock-invocationMetrics", last_chunk)
        metrics = last_chunk["amazon-bedrock-invocationMetrics"]
        self.assertIsInstance(metrics, dict)
        self.assertIn("inputTokenCount", metrics)
        self.assertGreater(metrics["inputTokenCount"], 0)
        self.assertIn("outputTokenCount", metrics)
        self.assertGreater(metrics["outputTokenCount"], 0)

    @parameterized.expand(
        [
            AMAZON_NOVA_PREMIER_TEST_MODEL,
            CLAUDE_4_5_SONNET_TEST_MODEL
        ]
    )
    async def test_async_amazon_bedrock_converse(self, model):
        session = AsyncSession()
        bedrock = await session.async_client(model_name=model)
        conversation = [
            {
                "role": "user",
                "content": [
                    {
                        "text": "Describe the purpose of a 'hello world' program in one line."
                    }
                ],
            }
        ]

        response = await bedrock.converse(
            messages=conversation,
            inferenceConfig={"maxTokens": 512, "temperature": 0.0},
        )
        self.assertIsInstance(response, dict)
        self.assertEqual(response["ResponseMetadata"]["HTTPStatusCode"], 200)
        self.assertIsInstance(response["output"]["message"]["content"][0]["text"], str)

    @parameterized.expand(
        [
            AMAZON_NOVA_PREMIER_TEST_MODEL,
            CLAUDE_4_5_SONNET_TEST_MODEL
        ]
    )
    async def test_async_amazon_bedrock_converse_stream(self, model):
        session = AsyncSession()
        bedrock = await session.async_client(model_name=model)
        conversation = [
            {
                "role": "user",
                "content": [
                    {
                        "text": "Describe the purpose of a 'hello world' program in one line."
                    }
                ],
            }
        ]

        response = await bedrock.converse_stream(
            messages=conversation,
            inferenceConfig={"maxTokens": 512, "temperature": 0.0},
        )

        stream = response['stream']
        response_metadata = response['ResponseMetadata']
        self.assertIsInstance(response_metadata, dict)
        self.assertIn('HTTPHeaders', response_metadata)
        self.assertIsInstance(response_metadata['HTTPHeaders'], dict)
        headers = response_metadata['HTTPHeaders']
        self.assertIn('content-type', headers)
        self.assertEqual(headers['content-type'], 'application/vnd.amazon.eventstream')
        number_of_chunks = 0
        last_three_chunks = []
        async for chunk in stream:
            number_of_chunks += 1
            if number_of_chunks == 1:
                self.assertIn('messageStart', chunk)
            if 'contentBlockDelta' in chunk:
                delta = chunk['contentBlockDelta']
                self.assertIsInstance(delta, dict)
                if 'text' in delta:
                    text = delta['text']
                    self.assertIsInstance(text, str)
            last_three_chunks.append(chunk)
            if len(last_three_chunks) > 3:
                last_three_chunks.pop(0)
        content_block_stop = last_three_chunks[0]
        self.assertIn('contentBlockStop', content_block_stop)
        message_stop = last_three_chunks[1]
        self.assertIn('messageStop', message_stop)
        metadata = last_three_chunks[2]
        self.assertIn('metadata', metadata)
        metadata = metadata['metadata']
        self.assertIsInstance(metadata, dict)
        self.assertIn('usage', metadata)
        usage = metadata['usage']
        self.assertIsInstance(usage, dict)
        self.assertIn('inputTokens', usage)
        self.assertIn('outputTokens', usage)
        self.assertIn('totalTokens', usage)

    async def test_async_amazon_titan_embedding(self):
        session = AsyncSession()
        bedrock = await session.async_client(model_name=AMAZON_TITAN_EMBEDDING_TEST_MODEL)
        body = json.dumps(
            {
                "inputText": "Please recommend books with a theme similar to the movie 'Inception'.",
            }
        )
        response = await bedrock.invoke_model(
            body=body,
        )
        response_body = json.loads(await response.get("body").read())
        self.assertIsInstance(response, dict)
        self.assertEqual(response["ResponseMetadata"]["HTTPStatusCode"], 200)
        self.assertIsInstance(response_body["embedding"], list)
        self.assertTrue(
            all(isinstance(item, float) for item in response_body["embedding"])
        )
