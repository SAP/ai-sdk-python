import unittest

from integration_tests.constants import NVIDIA_EMBEDDING_TEST_MODEL
from tests.mock import (
    get_mocked_ai_core_client,
    openai_chat_completion_mocker,
    openai_completion_mocker,
    openai_embeddings_mocker,
    cohere_chat_completion_mocker,
)

try:
    import openai as _

    no_openai = False
except ImportError as err:
    no_openai = True

try:
    from langchain_classic.chains import LLMChain
    from langchain_classic.prompts.chat import (
        AIMessagePromptTemplate,
        ChatPromptTemplate,
        HumanMessagePromptTemplate,
        SystemMessagePromptTemplate,
    )

    from gen_ai_hub.proxy.langchain.openai import ChatOpenAI, OpenAI, OpenAIEmbeddings

    no_langchain = False
except ImportError as err:
    no_langchain = True


@unittest.skipIf(no_openai or no_langchain, 'langchain or openai not installed')
class TestOpenAILangchain(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.proxy_client = get_mocked_ai_core_client()

    def test_embedding_model(self):
        deployment = self.proxy_client.select_deployment(model_name='text-embedding-ada-002')

        with openai_embeddings_mocker(deployment.prediction_url):
            embedding_model = OpenAIEmbeddings(proxy_client=self.proxy_client,
                                               proxy_model_name='text-embedding-ada-002')
            self.assertIsNotNone(embedding_model.model)
            response = embedding_model.embed_query('Your text string goes here')
            self.assertIsInstance(response, list)
            self.assertTrue(all(isinstance(item, float) for item in response))

    def test_nvidia_embedding(self, model=NVIDIA_EMBEDDING_TEST_MODEL):
        deployment = self.proxy_client.select_deployment(model_name=model)

        with openai_embeddings_mocker(deployment.prediction_url):
            # Test without input_type parameter
            with self.assertRaises(ValueError) as cm:
                embedding_model = OpenAIEmbeddings(proxy_client=self.proxy_client,
                                                   proxy_model_name=model)
                embedding_model.embed_query('Your text string goes here')
            
            self.assertIn("input_type parameter is required", str(cm.exception))
            self.assertIn(model, str(cm.exception))
            
            # Test with proper input_type parameter
            embedding_model = OpenAIEmbeddings(
                proxy_client=self.proxy_client,
                proxy_model_name=model,
                input_type='query'
            )
            self.assertIsNotNone(embedding_model.model)
            response = embedding_model.embed_query('Your text string goes here')
            self.assertIsInstance(response, list)
            self.assertTrue(all(isinstance(item, float) for item in response))

    def test_completion_model(self):
        deployment = self.proxy_client.select_deployment(model_name='gpt-4-instruct')
        deployment.prediction_urls.register({'gpt-4-instruct':
                                                 '/completions'})  # Add it to test completion model
        with openai_completion_mocker(deployment.prediction_url):
            llm = OpenAI(proxy_client=self.proxy_client, proxy_model_name='gpt-4-instruct')
            self.assertIsNotNone(llm.model_name)
            response = llm.invoke('Your text string goes here')
            self.assertIsInstance(response, str)

    def test_chat_model_cohere(self, model_name='cohere--command-a-reasoning'):
        deployment = self.proxy_client.select_deployment(model_name=model_name)

        with cohere_chat_completion_mocker(deployment.prediction_url):
            self._test_chat_model(model_name)

    def _test_chat_model(self, model_name: str):
        chat_model = ChatOpenAI(proxy_client=self.proxy_client, proxy_model_name=model_name)
        self.assertIsNotNone(chat_model.model_name)
        template = 'You are a helpful assistant that translates english to pirate.'

        system_message_prompt = SystemMessagePromptTemplate.from_template(template)

        example_human = HumanMessagePromptTemplate.from_template('Hi')
        example_ai = AIMessagePromptTemplate.from_template('Ahoy!')
        human_template = '{text}'

        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        chat_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, example_human, example_ai, human_message_prompt])

        chain = LLMChain(llm=chat_model, prompt=chat_prompt)
        response = chain.invoke('I love programming')
        self.assertIsInstance(response['text'], str)

    def test_chat_model(self, model_name='gpt-4o-mini'):
        deployment = self.proxy_client.select_deployment(model_name=model_name)

        with openai_chat_completion_mocker(deployment.prediction_url):
            self._test_chat_model(model_name)

    def test_client_params(self):
        with self.assertRaises(ValueError):
            OpenAI(proxy_client=self.proxy_client, proxy_model_name='gpt-4-instruct', n=0)
        with self.assertRaises(ValueError):
            OpenAI(proxy_client=self.proxy_client, proxy_model_name='gpt-4-instruct', n=2, streaming=True)
        with self.assertRaises(ValueError):
            ChatOpenAI(proxy_client=self.proxy_client, proxy_model_name='gpt-4o-mini', n=0)
        with self.assertRaises(ValueError):
            ChatOpenAI(proxy_client=self.proxy_client, proxy_model_name='gpt-4o-mini', n=2, streaming=True)

    def test_max_completion_token(self):
        unexpected_keyword_exception_message = "got an unexpected keyword argument"
        with self.assertRaises(TypeError) as cm:
            chat_open_api = ChatOpenAI(proxy_client=self.proxy_client, proxy_model_name='gpt-4o-mini', n=1,
                                       unexpected_token_kwarg=1)
            chat_open_api.invoke('test invocation')
        self.assertIsInstance(cm.exception, TypeError)
        self.assertIn(unexpected_keyword_exception_message, str(cm.exception))

        with self.assertRaises(BaseException) as cm:
            chat_open_api = ChatOpenAI(proxy_client=self.proxy_client, proxy_model_name='gpt-4o-mini', n=1,
                                       max_completion_tokens=1)
            chat_open_api.invoke('test invocation')
        self.assertNotIn(unexpected_keyword_exception_message, str(cm.exception))

    def test_chat_openai_preserves_root_client(self):
        """Test that ChatOpenAI preserves the root client when using native OpenAI client"""
        from gen_ai_hub.proxy.native.openai import OpenAI as NativeOpenAI

        native_client = NativeOpenAI(proxy_client=self.proxy_client)

        chat_model = ChatOpenAI(
            client=native_client,
            proxy_client=self.proxy_client,
            proxy_model_name='gpt-4o-mini'
        )

        # Verify root_client is preserved
        self.assertTrue(hasattr(chat_model, 'root_client'))
        self.assertEqual(chat_model.root_client, native_client)

        # Verify client points to chat.completions
        self.assertEqual(chat_model.client, native_client.chat.completions)

    def test_chat_openai_preserves_root_async_client(self):
        """Test that ChatOpenAI preserves the root async client when using native async OpenAI client"""
        from gen_ai_hub.proxy.native.openai import AsyncOpenAI as NativeAsyncOpenAI

        native_async_client = NativeAsyncOpenAI(proxy_client=self.proxy_client)

        chat_model = ChatOpenAI(
            async_client=native_async_client,
            proxy_client=self.proxy_client,
            proxy_model_name='gpt-4o-mini'
        )

        # Verify root_async_client is preserved
        self.assertTrue(hasattr(chat_model, 'root_async_client'))
        self.assertEqual(chat_model.root_async_client, native_async_client)

        # Verify async_client points to chat.completions
        self.assertEqual(chat_model.async_client, native_async_client.chat.completions)

    def test_openai_completion_preserves_root_client(self):
        """Test that OpenAI completion model preserves the root client"""
        from gen_ai_hub.proxy.native.openai import OpenAI as NativeOpenAI

        native_client = NativeOpenAI(proxy_client=self.proxy_client)

        completion_model = OpenAI(
            client=native_client,
            proxy_client=self.proxy_client,
            proxy_model_name='gpt-4o-mini'
        )

        # Verify root_client is preserved (it may be in model_kwargs due to pydantic validation)
        self.assertTrue(hasattr(completion_model, 'root_client') or 'root_client' in completion_model.model_kwargs)
        if hasattr(completion_model, 'root_client'):
            self.assertEqual(completion_model.root_client, native_client)
        else:
            self.assertEqual(completion_model.model_kwargs['root_client'], native_client)

        # Verify client points to completions
        self.assertEqual(completion_model.client, native_client.completions)

    def test_openai_completion_preserves_root_async_client(self):
        """Test that OpenAI completion model preserves the root async client"""
        from gen_ai_hub.proxy.native.openai import AsyncOpenAI as NativeAsyncOpenAI

        native_async_client = NativeAsyncOpenAI(proxy_client=self.proxy_client)

        completion_model = OpenAI(
            async_client=native_async_client,
            proxy_client=self.proxy_client,
            proxy_model_name='gpt-4o-mini'
        )

        # Verify root_async_client is preserved (it may be in model_kwargs due to pydantic validation)
        self.assertTrue(
            hasattr(completion_model, 'root_async_client') or 'root_async_client' in completion_model.model_kwargs)
        if hasattr(completion_model, 'root_async_client'):
            self.assertEqual(completion_model.root_async_client, native_async_client)
        else:
            self.assertEqual(completion_model.model_kwargs['root_async_client'], native_async_client)

        # Verify async_client points to completions
        self.assertEqual(completion_model.async_client, native_async_client.completions)
