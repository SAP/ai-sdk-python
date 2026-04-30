import unittest

import pytest
from langchain_classic.chains import LLMChain
from langchain_classic.prompts.chat import (
    AIMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.messages import AIMessage, HumanMessage, AIMessageChunk
from parameterized import parameterized
from pydantic import BaseModel

from gen_ai_hub.proxy.langchain.amazon import BedrockEmbeddings, ChatBedrock, ChatBedrockConverse
from integration_tests.constants import (AMAZON_TITAN_EMBEDDING_TEST_MODEL, CLAUDE_4_5_SONNET_TEST_MODEL,
                                         AMAZON_NOVA_PREMIER_TEST_MODEL, AMAZON_NOVA_MICRO_TEST_MODEL,
                                         CLAUDE_3_7_SONNET_TEST_MODEL, CLAUDE_4_5_HAIKU_TEST_MODEL)
from integration_tests.setup_aicore import TestCaseAICoreSetupMixin, TestCaseBedrockSetupMixin

@pytest.mark.bedrock
class TestAmazonLLM(TestCaseAICoreSetupMixin, unittest.TestCase):
    """
    Titan models were retired and replaced by (multimodal) nova models.
    Documentation on nova models: https://docs.aws.amazon.com/nova/latest/userguide/what-is-nova.html
    https://docs.aws.amazon.com/bedrock/latest/userguide/inference-methods.html
    """

    def test_invoke(self, model=CLAUDE_4_5_SONNET_TEST_MODEL):
        with self.subTest(model=model):
            chat_model = ChatBedrock(
                model_name=model,
                model_kwargs={"temperature": 0.0},
                proxy_client=self.proxy_client,
            )
            template = "You are a helpful assistant that translates english to pirate."

            system_message_prompt = SystemMessagePromptTemplate.from_template(template)

            example_human = HumanMessagePromptTemplate.from_template("Hi")
            example_ai = AIMessagePromptTemplate.from_template("Ahoy!")
            human_template = "{text}"

            human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
            chat_prompt = ChatPromptTemplate.from_messages(
                [system_message_prompt, example_human, example_ai, human_message_prompt]
            )

            chain = LLMChain(llm=chat_model, prompt=chat_prompt)
            response = chain.invoke("I love programming")
            self.assertIsInstance(response["text"], str)

    def test_converse(self, model=AMAZON_NOVA_MICRO_TEST_MODEL):
        with self.subTest(model=model):
            chat_model = ChatBedrockConverse(
                model_name=model,
                model_kwargs={"temperature": 0.0},
                proxy_client=self.proxy_client,
            )
            template = "You are a helpful assistant that translates english to pirate."

            system_message_prompt = SystemMessagePromptTemplate.from_template(template)

            example_human = HumanMessagePromptTemplate.from_template("Hi")
            example_ai = AIMessagePromptTemplate.from_template("Ahoy!")
            human_template = "{text}"

            human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
            chat_prompt = ChatPromptTemplate.from_messages(
                [system_message_prompt, example_human, example_ai, human_message_prompt]
            )

            chain = LLMChain(llm=chat_model, prompt=chat_prompt)
            response = chain.invoke("I love programming")
            self.assertIsInstance(response["text"], str)

    @parameterized.expand(
        [
            CLAUDE_4_5_SONNET_TEST_MODEL,
            CLAUDE_4_5_HAIKU_TEST_MODEL,
        ]
    )
    def test_stream(self, model= CLAUDE_4_5_SONNET_TEST_MODEL):
        with self.subTest(model=model):
            chat_model = ChatBedrock(
                model_name=model,
                model_kwargs={"temperature": 0.0},
                proxy_client=self.proxy_client,
                streaming=True
            )

            chunks = [chunk for chunk in chat_model.stream([HumanMessage(content="Why is the sky blue?")])]
            self.assertTrue(all(isinstance(chunk, AIMessageChunk) for chunk in chunks))
            if "anthropic" in model:  # Token by token streaming is only supported for anthropic models
                self.assertGreater(len(chunks), 1, "Only one chunk received - stream seems to be buffered.")

    def test_embed_query(self):
        embedding_model = BedrockEmbeddings(
            model_name=AMAZON_TITAN_EMBEDDING_TEST_MODEL, proxy_client=self.proxy_client
        )
        response = embedding_model.embed_query("Your text string goes here")
        self.assertIsInstance(response, list)
        self.assertTrue(all(isinstance(item, float) for item in response))

    def test_structured_output(self):

        class Mountain(BaseModel):
            name: str
            country: str
            height_in_meters: int

        chat_model = ChatBedrock(
            model_name=CLAUDE_3_7_SONNET_TEST_MODEL,
            model_kwargs={"temperature": 0.0},
            proxy_client=self.proxy_client,
        )

        chat_model = chat_model.with_structured_output(Mountain)
        mountain = chat_model.invoke(
            [HumanMessage(content="What is the highest mountain in Japan?")]
        )

        self.assertIsInstance(mountain, Mountain)
        self.assertIn("Fuji", mountain.name)
        self.assertEqual(mountain.country, "Japan")
        self.assertAlmostEqual(mountain.height_in_meters, 3776, delta=100)


@pytest.mark.bedrock
class TestAmazonLLMAsync(TestCaseBedrockSetupMixin, unittest.IsolatedAsyncioTestCase):

    async def test_chat_model(self):
        chat_model = ChatBedrock(
            model_name=CLAUDE_4_5_SONNET_TEST_MODEL,
            model_kwargs={"temperature": 0.0},
            proxy_client=self.proxy_client,
        )
        response = await chat_model.ainvoke(
            [HumanMessage(content="Write me a song about sparkling water.")]
        )
        self.assertIsInstance(response, AIMessage)

    async def test_chat_converse_model(self, model=AMAZON_NOVA_MICRO_TEST_MODEL):
        with self.subTest(model=model):
            chat_model = ChatBedrockConverse(
                model_name=model,
                model_kwargs={"temperature": 0.0},
                proxy_client=self.proxy_client,
            )
            response = await chat_model.ainvoke(
                [HumanMessage(content="Write me a song about sparkling water.")]
            )
            self.assertIsInstance(response, AIMessage)

    async def test_async_chat_streaming(self):
        from langchain_classic.schema import HumanMessage
        chat_model = ChatBedrock(
            model_name=CLAUDE_4_5_SONNET_TEST_MODEL,
            model_kwargs={"temperature": 0.0},
            proxy_client=self.proxy_client,
            streaming=True
        )
        chunks = [chunk async for chunk
                  in chat_model.astream([HumanMessage(content='Write me a song about sparkling water.')])]
        self.assertTrue(all(isinstance(chunk, AIMessageChunk) for chunk in chunks))
        self.assertGreater(len(chunks), 1, "Only one chunk received - stream seems to be buffered.")
