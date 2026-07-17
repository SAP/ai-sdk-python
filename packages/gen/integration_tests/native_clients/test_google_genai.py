import unittest

from google.genai.types import GenerateContentResponse, GenerateContentConfig, Content, EmbedContentResponse, Part

from gen_ai_hub.proxy.native.google_genai.clients import Client
from integration_tests.constants import GEMINI_2_5_FLASH_LITE_TEST_MODEL, GOOGLE_EMBEDDING_TEST_MODEL
from integration_tests.setup_aicore import TestCaseAICoreSetupMixin


def get_test_messages(text="Write a story about a magic backpack."):
    if not text:
        text = "Write a story about a magic backpack."
    user_prompt_content = Content(
        role="user",
        parts=[
            Part(text=text),
        ],
    )
    return [user_prompt_content]


class GoogleGenAITests(TestCaseAICoreSetupMixin, unittest.TestCase):

    def test_client_discovery(self):
        google_deployments = [
            deployment
            for deployment in self.proxy_client.deployments
            if any(element in deployment.model_name for element in ["gemini"])
        ]
        self.assertGreater(
            len(google_deployments), 0, "No google virtual deployments found"
        )

    def test_genai_chat(self):
        client = Client(proxy_client=self.proxy_client)
        chat_session = client.chats.create(
            model=GEMINI_2_5_FLASH_LITE_TEST_MODEL
        )
        model_response = chat_session.send_message("Hello.")
        self.assertIsInstance(model_response, GenerateContentResponse)
        model_response = chat_session.send_message(
            "I am also fine. What are your plans for today?"
        )
        self.assertIsInstance(model_response, GenerateContentResponse)

    def test_genai_generate_content(self):
        client = Client(proxy_client=self.proxy_client)
        response = client.models.generate_content(
            model=GEMINI_2_5_FLASH_LITE_TEST_MODEL,
            contents=get_test_messages(),
            config=GenerateContentConfig(temperature=0),
        )
        self.assertIsInstance(response, GenerateContentResponse)

    def test_genai_stream_generate_content(self):
        client = Client(proxy_client=self.proxy_client)
        response = client.models.generate_content_stream(
            model=GEMINI_2_5_FLASH_LITE_TEST_MODEL,
            contents=get_test_messages(
                text="You are a story teller. Write a paragraph about a magic kingdom."
            ),
            config=GenerateContentConfig(temperature=0),
        )
        chunks = [chunk for chunk in response]
        self.assertTrue(all(isinstance(chunk.text, str) for chunk in chunks))
        self.assertGreater(len(chunks), 1, "Only one chunk received - stream seems to be buffered.")

    def test_genai_embedding(self):
        client = Client(proxy_client=self.proxy_client)
        response = client.models.embed_content(
            model=GOOGLE_EMBEDDING_TEST_MODEL,
            contents="What's the meaning of life?"
        )
        self.assertIsInstance(response, EmbedContentResponse)

    def test_genai_embedding_model_name_with_version(self):
        client = Client(proxy_client=self.proxy_client)
        response = client.models.embed_content(
            model=f"{GOOGLE_EMBEDDING_TEST_MODEL}-001",
            contents="What's the meaning of life?"
        )
        self.assertIsInstance(response, EmbedContentResponse)

class AsyncGoogleGenAITests(TestCaseAICoreSetupMixin, unittest.IsolatedAsyncioTestCase):

    async def test_genai_generate_content_async(self):
        async with Client(proxy_client=self.proxy_client).aio as aclient:
            response = await aclient.models.generate_content(
                model=GEMINI_2_5_FLASH_LITE_TEST_MODEL,
                contents=get_test_messages(),
                config=GenerateContentConfig(temperature=0),
            )
            self.assertIsInstance(response, GenerateContentResponse)

    async def test_genai_chat_async(self):
        async with Client(proxy_client=self.proxy_client).aio as aclient:
            chat_session = aclient.chats.create(
                model=GEMINI_2_5_FLASH_LITE_TEST_MODEL
            )
            model_response = await chat_session.send_message("Hello.")
            self.assertIsInstance(model_response, GenerateContentResponse)
            model_response = await chat_session.send_message(
                "What is your opinion about latest Gemini model?"
            )
            self.assertIsInstance(model_response, GenerateContentResponse)

    async def test_genai_stream_generate_content_async(self):
        async with Client(proxy_client=self.proxy_client).aio as aclient:
            async_response_stream = await aclient.models.generate_content_stream(
                model=GEMINI_2_5_FLASH_LITE_TEST_MODEL,
                contents=get_test_messages(
                    text="You are a story teller. Write a paragraph about a magic kingdom."
                ),
                config=GenerateContentConfig(temperature=0),
            )
            chunks = [chunk async for chunk in async_response_stream]
            self.assertTrue(all(isinstance(chunk.text, str) for chunk in chunks))
            self.assertGreater(len(chunks), 1, "Only one chunk received - stream seems to be buffered.")


if __name__ == "__main__":
    unittest.main()
