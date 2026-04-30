import unittest

from parameterized import parameterized
from pydantic import BaseModel

from integration_tests.constants import OPENAI_GPT_O4_MINI_TEST_MODEL, \
    OPENAI_GPT_4O_MINI_TEST_MODEL, OPENAI_GPT_5_TEST_MODEL, OPENAI_EMBEDDING_TEST_MODEL, OPENAI_GPT_O3_MINI_TEST_MODEL, \
    MISTRAL_TEST_MODEL, NVIDIA_EMBEDDING_TEST_MODEL, PERPLEXITY_TEST_MODEL, COHERE_COMMAND_A_TEST_MODEL, COHERE_RERANK_TEST_MODEL
from integration_tests.setup_aicore import TestCaseAICoreSetupMixin

try:
    import openai

    no_openai = False
except ImportError:
    no_openai = True
try:
    from gen_ai_hub.proxy.langchain.openai import ChatOpenAI, OpenAIEmbeddings
    from langchain_classic.chains import LLMChain
    from langchain_classic.prompts.chat import (
        AIMessagePromptTemplate,
        ChatPromptTemplate,
        HumanMessagePromptTemplate,
    )
    from langchain_classic.schema import AIMessage, HumanMessage
    from langchain_core.messages.ai import AIMessageChunk

    no_langchain = False
except ImportError:
    no_langchain = True


class Person(BaseModel):
    """
    A simple Pydantic model to test structured outputs with LangChain.
    """
    name: str
    age: int


@unittest.skipIf(no_openai or no_langchain, 'langchain or openai not installed')
class TestOpenAILLM(TestCaseAICoreSetupMixin, unittest.TestCase):

    @parameterized.expand(
        [
            OPENAI_GPT_O4_MINI_TEST_MODEL,
            PERPLEXITY_TEST_MODEL,
        ]
    )
    def test_chat_model(self, model=OPENAI_GPT_4O_MINI_TEST_MODEL):
        chat_model = ChatOpenAI(proxy_model_name=model, proxy_client=self.proxy_client, max_retries=10)
        self.assertIsNotNone(chat_model.model_name)

        example_human = HumanMessagePromptTemplate.from_template('Hi')
        example_ai = AIMessagePromptTemplate.from_template('Ahoy!')
        human_template = '{text}'

        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        chat_prompt = ChatPromptTemplate.from_messages(
            [example_human, example_ai, human_message_prompt]
        )

        chain = LLMChain(llm=chat_model, prompt=chat_prompt)
        response = chain.invoke('I love programming')
        self.assertIsInstance(response['text'], str)

    def test_chat_model_streaming(self, model=OPENAI_GPT_5_TEST_MODEL):
        from langchain_classic.schema import HumanMessage
        chat = ChatOpenAI(proxy_client=self.proxy_client,
                          proxy_model_name=model,
                          streaming=True,
                          temperature=0,
                          max_retries=10)
        chunks = [*chat.stream([HumanMessage(content='Write me a song about sparkling water.')])]
        self.assertIsNotNone(chat.model_name)
        self.assertTrue(all(isinstance(chunk, AIMessageChunk) for chunk in chunks))
        self.assertGreater(len(chunks), 1, "Only one chunk received - stream seems to be buffered.")

    def test_embedding_model(self, model=OPENAI_EMBEDDING_TEST_MODEL):
         embedding_model = OpenAIEmbeddings(proxy_model_name=model, proxy_client=self.proxy_client)
         self.assertIsNotNone(embedding_model.model)
         response = embedding_model.embed_query('Your text string goes here')
         self.assertIsInstance(response, list)
         self.assertTrue(all(isinstance(item, float) for item in response))

    def test_nvidia_embedding_model(self):
        embedding_model = OpenAIEmbeddings(
            proxy_client=self.proxy_client,
            proxy_model_name=NVIDIA_EMBEDDING_TEST_MODEL,
            input_type='query'
        )
        self.assertIsNotNone(embedding_model.model)
        response = embedding_model.embed_query('Your text string goes here')
        self.assertIsInstance(response, list)
        self.assertTrue(all(isinstance(item, float) for item in response))


    def test_structured_outputs(self, model=OPENAI_GPT_4O_MINI_TEST_MODEL):
        chat_model = ChatOpenAI(proxy_model_name=model, proxy_client=self.proxy_client, max_retries=10)
        chat_model = chat_model.with_structured_output(method="json_schema", schema=Person, strict=True)

        message = HumanMessage(content="Tell me about a person named John who is 30")
        response = chat_model.invoke([message])
        self.assertIsInstance(response, Person)

    def test_cohere_command_a_reasoning(self, model=COHERE_COMMAND_A_TEST_MODEL):
        """Test Cohere Command-A reasoning model via OpenAI compatibility API."""
        chat_model = ChatOpenAI(proxy_model_name=model, proxy_client=self.proxy_client, temperature=0.5, max_tokens=100,
                                max_retries=10)
        message = HumanMessage(content='Explain the concept of recursion in programming.')
        response = chat_model.invoke([message])
        self.assertIsInstance(response, AIMessage)
        self.assertIsNotNone(response.content)

    def test_cohere_rerank(self, model=COHERE_RERANK_TEST_MODEL):
        """Test Cohere Command-A reasoning model via OpenAI compatibility API."""
        chat_model = ChatOpenAI(proxy_model_name=model, proxy_client=self.proxy_client, temperature=0.5, max_tokens=100,
                                max_retries=10)
        message = HumanMessage(content='Explain the concept of recursion in programming.')
        response = chat_model.invoke([message])
        self.assertIsInstance(response, AIMessage)
        self.assertIsNotNone(response.content)


@unittest.skipIf(no_openai, 'openai not installed')
class AsyncOpenAITests(TestCaseAICoreSetupMixin, unittest.IsolatedAsyncioTestCase):

    @parameterized.expand(
        [
            OPENAI_GPT_O3_MINI_TEST_MODEL,
            MISTRAL_TEST_MODEL,
        ]
    )
    async def test_chat_model(self, model=OPENAI_GPT_4O_MINI_TEST_MODEL):
        chat_model = ChatOpenAI(proxy_model_name=model, proxy_client=self.proxy_client, max_retries=10)
        self.assertIsNotNone(chat_model.model_name)
        response = await chat_model.ainvoke([HumanMessage(content='Write me a song about sparkling water.')])
        self.assertIsInstance(response, AIMessage)

    async def test_async_chat_streaming(self, model=OPENAI_GPT_4O_MINI_TEST_MODEL):
        from langchain_classic.schema import HumanMessage
        chat = ChatOpenAI(proxy_client=self.proxy_client,
                          proxy_model_name=model,
                          streaming=True,
                          temperature=1,
                          max_retries=10)
        chunks = [chunk async for chunk
                  in chat.astream([HumanMessage(content='Write me a song about sparkling water.')])]
        self.assertTrue(all(isinstance(chunk, AIMessageChunk) for chunk in chunks))
        self.assertGreater(len(chunks), 1, "Only one chunk received - stream seems to be buffered.")

    async def test_async_structured_outputs(self, model=OPENAI_GPT_4O_MINI_TEST_MODEL):
        chat_model = ChatOpenAI(proxy_model_name=model, proxy_client=self.proxy_client, max_retries=10)
        chat_model = chat_model.with_structured_output(method="json_schema", schema=Person, strict=True)

        message = HumanMessage(content="Tell me about a person named John who is 30")
        response = await chat_model.ainvoke([message])
        self.assertIsInstance(response, Person)


if __name__ == '__main__':
    unittest.main()
