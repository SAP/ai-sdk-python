import unittest
from unittest.mock import patch

from botocore.config import Config
from langchain_classic.chains import LLMChain
from langchain_classic.prompts import (
    AIMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

from gen_ai_hub.proxy.langchain.amazon import BedrockEmbeddings, ChatBedrock, ChatBedrockConverse, init_chat_model
from tests.mock import (
    AMAZON_TITAN_EMBED_QUERY_RESPONSE,
    AMAZON_BEDROCK_INVOKE_RESPONSE,
    get_mocked_ai_core_client,
)


class TestAmazonLangchain(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.proxy_client = get_mocked_ai_core_client()

    def test_model_kwargs(self):
        model_kwargs = {"top_k": 3, "stop_sequences": ["abc"]}
        chat_model = init_chat_model(self.proxy_client,
                                     deployment=self.proxy_client.select_deployment(
                                         model_name='amazon--nova-premier'),
                                     **model_kwargs)
        self.assertIsInstance(chat_model, ChatBedrock)

    @patch("langchain_classic.chains.base.Chain.invoke")
    def test_chat_model(self, mock_chain_invoke):
        mock_chain_invoke.return_value = AMAZON_BEDROCK_INVOKE_RESPONSE
        chat_model = ChatBedrock(
            model_name="amazon--nova-premier", proxy_client=self.proxy_client
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

    @patch("langchain_community.embeddings.bedrock.BedrockEmbeddings.embed_query")
    def test_embedding_model(self, mock_chain_invoke):
        mock_chain_invoke.return_value = AMAZON_TITAN_EMBED_QUERY_RESPONSE
        embedding_model = BedrockEmbeddings(
            model_name="amazon--titan-embed-text", proxy_client=self.proxy_client
        )
        response = embedding_model.embed_query("Your text string goes here")
        self.assertIsInstance(response["embedding"], list)
        self.assertTrue(all(isinstance(item, float) for item in response["embedding"]))

    def test_no_model_id(self):
        with self.assertRaises(ValueError):
            BedrockEmbeddings(proxy_client=self.proxy_client)
        with self.assertRaises(ValueError):
            ChatBedrock(proxy_client=self.proxy_client)
        with self.assertRaises(ValueError):
            ChatBedrockConverse(proxy_client=self.proxy_client)

    def test_no_model_name(self):
        with self.assertRaises(ValueError):
            ChatBedrock.get_corresponding_model_id(model_name="")

    def test_model_id_not_empty(self):
        with self.assertRaises(ValueError):
            BedrockEmbeddings(model_id="abc", proxy_client=self.proxy_client)
        with self.assertRaises(ValueError):
            ChatBedrock(model_id="abc", proxy_client=self.proxy_client)
        with self.assertRaises(ValueError):
            ChatBedrockConverse(model_id="abc", proxy_client=self.proxy_client)

    @patch("langchain_classic.chains.base.Chain.invoke")
    def test_chat_converse(self, mock_chain_invoke):
        mock_chain_invoke.return_value = AMAZON_BEDROCK_INVOKE_RESPONSE
        chat_model = ChatBedrockConverse(
            model_name="amazon--nova-premier", proxy_client=self.proxy_client,
            model="amazon--nova-premier"
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

    def test_chat_model_config(self):
        boto_config = Config(
            connect_timeout=59,
            read_timeout=299,
        )

        chat_model = ChatBedrockConverse(
            model_name="amazon--nova-premier", proxy_client=self.proxy_client,
            model="amazon--nova-premier",
            config=boto_config
        )
        self.assertTrue(chat_model.client.meta.config.read_timeout == 299,
                        "Read Timeout not applied")

        self.assertTrue(chat_model.client.meta.config.connect_timeout == 59,
                        "Connect Timeout not applied")



