import unittest
from unittest.mock import patch

from langchain_classic.chains import LLMChain
from langchain_classic.prompts.chat import (
    AIMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

from gen_ai_hub.proxy.langchain.google_genai import ChatGoogleGenerativeAI
from tests.mock import GOOGLE_GEMINI_INVOKE_RESPONSE, get_mocked_ai_core_client


class TestGoogleGenerativeAILangchain(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.proxy_client = get_mocked_ai_core_client()

    @patch("langchain_classic.chains.base.Chain.invoke")
    def test_chat_model(self, mock_chain_invoke):
        mock_chain_invoke.return_value = GOOGLE_GEMINI_INVOKE_RESPONSE
        chat_model = ChatGoogleGenerativeAI(
            proxy_model_name="gemini-2.0-flash", proxy_client=self.proxy_client
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

    def test_model_id_not_empty(self):
        with self.assertRaises(ValueError):
            ChatGoogleGenerativeAI(model_id="abc")
