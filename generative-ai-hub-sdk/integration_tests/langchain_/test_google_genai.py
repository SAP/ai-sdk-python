import unittest
import uuid

from langchain_classic.chains import LLMChain
from langchain_classic.prompts import PromptTemplate
from langchain_classic.prompts.chat import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_classic.schema import BaseChatMessageHistory, HumanMessage
from langchain_community.chat_message_histories.in_memory import ChatMessageHistory
from langchain_core.messages import AIMessage
from langchain_core.runnables.history import RunnableWithMessageHistory

from gen_ai_hub.proxy.langchain import init_llm
from gen_ai_hub.proxy.langchain.google_genai import ChatGoogleGenerativeAI
from gen_ai_hub.proxy.langchain.google_genai import GoogleGenerativeAIEmbeddings
from integration_tests.constants import GEMINI_2_FLASH_TEST_MODEL, \
    GOOGLE_EMBEDDING_TEST_MODEL, GEMINI_2_5_FLASH_LITE_TEST_MODEL
from integration_tests.setup_aicore import TestCaseAICoreSetupMixin


class TestGoogleGenerativeAI(TestCaseAICoreSetupMixin, unittest.TestCase):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.model_histories = {}

    def _get_model_history(self, session_id: str) -> BaseChatMessageHistory:
        return self.model_histories[session_id]

    def _create_model_history(self) -> str:
        session_id = str(uuid.uuid4())
        self.model_histories[session_id] = ChatMessageHistory()
        return session_id

    def test_genai_invoke(self, model=GEMINI_2_5_FLASH_LITE_TEST_MODEL):
        chat_model = ChatGoogleGenerativeAI(
            proxy_model_name=model,
            proxy_client=self.proxy_client,
            temperature=0
        )
        response = chat_model.invoke("Write a ballad about LangChain")
        self.assertIsInstance(response.content, str)

    def test_genai_embedding(self, model=GOOGLE_EMBEDDING_TEST_MODEL):
        embedding_model = GoogleGenerativeAIEmbeddings(
            proxy_model_name=model,
            proxy_client=self.proxy_client,
        )
        vector = embedding_model.embed_query("hello, world!")
        self.assertIsInstance(vector, list)
        self.assertTrue(all(isinstance(x, float) for x in vector))

    def test_genai_embedding_model_with_version(self, model=GOOGLE_EMBEDDING_TEST_MODEL):
        embedding_model = GoogleGenerativeAIEmbeddings(
            proxy_model_name=f'{model}-001',
            proxy_client=self.proxy_client,
        )
        vector = embedding_model.embed_query("hello, world!")
        self.assertIsInstance(vector, list)
        self.assertTrue(all(isinstance(x, float) for x in vector))

    def test_genai_stream(self, model=GEMINI_2_FLASH_TEST_MODEL):
        chat_model = ChatGoogleGenerativeAI(
            proxy_model_name=model,
            proxy_client=self.proxy_client,
            temperature=0
        )
        response = chat_model.stream(
            "You are a story teller. Write a story about a magic backpack."
        )
        chunks = [chunk for chunk in response]
        self.assertTrue(all(isinstance(chunk.content, str) for chunk in chunks))
        self.assertGreater(len(chunks), 1, "Only one chunk received - stream seems to be buffered.")

    def test_genai_langchain_history(self):
        chat_model = ChatGoogleGenerativeAI(
            proxy_model_name=GEMINI_2_5_FLASH_LITE_TEST_MODEL,
            proxy_client=self.proxy_client,
            temperature=0
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are the large language model {llmname}. Always say good bye in {topicprompt} fashion. Limit your response to 25 words max.",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ],
        )
        chat_model = prompt | chat_model

        history_id = self._create_model_history()
        config = {"configurable": {"session_id": history_id}}

        # first prompt
        model_with_message_history = RunnableWithMessageHistory(
            chat_model,
            self._get_model_history,
            input_messages_key="messages",
        )
        response = model_with_message_history.invoke(
            {
                "messages": [HumanMessage(content="My name is Jack Sparrow.")],
                "llmname": GEMINI_2_5_FLASH_LITE_TEST_MODEL,
                "topicprompt": "pirate",
            },
            config=config,
        )
        self.assertIsInstance(response.content, str)

        # second prompt
        response = model_with_message_history.invoke(
            {
                "messages": [HumanMessage(content="What is my name?")],
                "llmname": GEMINI_2_5_FLASH_LITE_TEST_MODEL,
                "topicprompt": "pirate",
            },
            config=config,
        )
        self.assertIsInstance(response.content, str)

    def test_chat_from_prompt_template(self):
        chat_model = ChatGoogleGenerativeAI(
            proxy_model_name=GEMINI_2_5_FLASH_LITE_TEST_MODEL,
            proxy_client=self.proxy_client,
            temperature=0
        )
        tweet_prompt = PromptTemplate.from_template(
            "You are a content creator. Write me a tweet about {topic}."
        )
        chain = LLMChain(llm=chat_model, prompt=tweet_prompt, verbose=True)
        response = chain.invoke("how bad could floods affect Heidelberg, Germany")
        self.assertIsInstance(response["text"], str)


class TestAsyncGoogleGenerativeAI(TestCaseAICoreSetupMixin, unittest.IsolatedAsyncioTestCase):

    async def test_genai_ainvoke(self):
        llm = init_llm(
            model_name=GEMINI_2_5_FLASH_LITE_TEST_MODEL,
            proxy_client=self.proxy_client,
            max_tokens=1000
        )
        response = await llm.ainvoke("Write a ballad about LangChain")
        self.assertIsInstance(response, AIMessage)

    async def test_genai_chat_ainvoke(self):
        chat_model = ChatGoogleGenerativeAI(
            model_name=GEMINI_2_5_FLASH_LITE_TEST_MODEL,
            proxy_client=self.proxy_client,
            max_tokens=1000
        )
        response = await chat_model.ainvoke("Write a ballad about LangChain")
        print(response)
        self.assertIsInstance(response, AIMessage)

    async def test_genai_astream(self):
        chat_model = ChatGoogleGenerativeAI(
            proxy_model_name=GEMINI_2_5_FLASH_LITE_TEST_MODEL,
            proxy_client=self.proxy_client,
            temperature=0
        )
        content = "You are a story teller. Write a story about a magic backpack."
        chunks = [chunk async for chunk in chat_model.astream(content)]
        self.assertTrue(all(isinstance(chunk.content, str) for chunk in chunks))
        self.assertGreater(len(chunks), 1, "Only one chunk received - stream seems to be buffered.")

if __name__ == "__main__":
    unittest.main()
