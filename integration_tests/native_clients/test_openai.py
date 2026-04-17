import unittest
from parameterized import parameterized
from pydantic import BaseModel

from integration_tests.constants import MISTRAL_TEST_MODEL, OPENAI_EMBEDDING_TEST_MODEL, \
    OPENAI_GPT_4_1_MINI_TEST_MODEL, OPENAI_GPT_O4_MINI_TEST_MODEL, OPENAI_GPT_4O_MINI_TEST_MODEL, \
    OPENAI_GPT_O3_MINI_TEST_MODEL, OPENAI_GPT_5_TEST_MODEL, NVIDIA_EMBEDDING_TEST_MODEL, PERPLEXITY_TEST_MODEL, COHERE_COMMAND_A_TEST_MODEL, \
    COHERE_RERANK_TEST_MODEL

try:
    import openai
    from gen_ai_hub.proxy.native.openai import AsyncOpenAI, OpenAI
    from gen_ai_hub.proxy.native.openai.clients import ChatCompletions
    from openai.types import Completion, CreateEmbeddingResponse
    from openai.types.chat import ChatCompletion, ChatCompletionChunk, ChatCompletionUserMessageParam

    no_openai = False
except ImportError:
    no_openai = True

from integration_tests.setup_aicore import TestCaseAICoreSetupMixin

class Person(BaseModel):
    """
    A simple Pydantic model for testing structured outputs with OpenAI.
    """
    name: str
    age: int


@unittest.skipIf(no_openai, 'openai not installed')
class OpenAITests(TestCaseAICoreSetupMixin, unittest.TestCase):

    def test_client_discovery(self):
        self.assertGreater(len(self.proxy_client.deployments), 0, 'No deployments found')

    def test_embedding(self, model=OPENAI_EMBEDDING_TEST_MODEL):
        kwargs = {'input': 'Your text string goes here', 'model_name': model}
        response = OpenAI(proxy_client=self.proxy_client, max_retries=10).embeddings.create(**kwargs)
        self.assertIsInstance(response, CreateEmbeddingResponse)
        response = OpenAI(proxy_client=self.proxy_client, max_retries=10).with_raw_response.embeddings.create(**kwargs)
        self.assertIsInstance(response, openai._legacy_response.LegacyAPIResponse)

    def test_embedding_global(self, model=OPENAI_EMBEDDING_TEST_MODEL):
        kwargs = {'input': 'Your text string goes here', 'model_name': model}
        from gen_ai_hub.proxy.native.openai import embeddings
        response = embeddings.create(**kwargs)
        self.assertIsInstance(response, CreateEmbeddingResponse)

    def test_nvidia_embedding(self, model=NVIDIA_EMBEDDING_TEST_MODEL):
        kwargs = {
            'input': 'Your text string goes here', 
            'model_name': model,
            'extra_body': {'input_type': 'query'} # NVIDIA embedding model requires input_type
        }
        response = OpenAI(proxy_client=self.proxy_client, max_retries=10).embeddings.create(**kwargs)
        self.assertIsInstance(response, CreateEmbeddingResponse)
        response = OpenAI(proxy_client=self.proxy_client, max_retries=10).with_raw_response.embeddings.create(**kwargs)
        self.assertIsInstance(response, openai._legacy_response.LegacyAPIResponse)

    # @parameterized.expand(
    #     [
    #         OPENAI_GPT_5_1_MINI_TEST_MODEL,
    #         OPENAI_GPT_O4_MINI_TEST_MODEL,
    #     ]
    # )
    def test_chat_completion(self, model=OPENAI_GPT_5_TEST_MODEL):
        messages = self._get_test_messages()
        kwargs = dict(model_name=model, messages=messages, max_completion_tokens=1024, seed=42)
        response = OpenAI(proxy_client=self.proxy_client, max_retries=10).chat.completions.create(**kwargs)
        self.assertIsInstance(response, ChatCompletion)
        response = OpenAI(proxy_client=self.proxy_client, max_retries=10).with_raw_response.chat.completions.create(
            **kwargs)
        self.assertIsInstance(response, openai._legacy_response.LegacyAPIResponse)

    def test_gpt_version_models(self, config_name="gpt-5-nano-latest"):
        messages = self._get_test_messages()
        kwargs = dict(config_name=config_name, messages=messages, temperature=0, seed=42)
        response = OpenAI(proxy_client=self.proxy_client, max_retries=10).chat.completions.create(**kwargs)
        self.assertIsInstance(response, ChatCompletion)
        response = OpenAI(proxy_client=self.proxy_client, max_retries=10).with_raw_response.chat.completions.create(
            **kwargs)
        self.assertIsInstance(response, openai._legacy_response.LegacyAPIResponse)

    def test_gpt_model_version_in_params(self, model_name=OPENAI_GPT_5_TEST_MODEL, model_version="latest"):
        messages = self._get_test_messages()
        kwargs = dict(model_name=model_name, model_version=model_version, messages=messages, temperature=0, seed=42)
        response = OpenAI(proxy_client=self.proxy_client, max_retries=10).chat.completions.create(**kwargs)
        self.assertIsInstance(response, ChatCompletion)
        response = OpenAI(proxy_client=self.proxy_client, max_retries=10).with_raw_response.chat.completions.create(
            **kwargs)
        self.assertIsInstance(response, openai._legacy_response.LegacyAPIResponse)

    def test_chat_completion_global(self, model=OPENAI_GPT_5_TEST_MODEL):
        from gen_ai_hub.proxy.native.openai import chat
        messages = self._get_test_messages()
        kwargs = dict(model_name=model, messages=messages, temperature=0, seed=42)
        response = chat.completions.create(**kwargs)
        self.assertIsInstance(response, ChatCompletion)

    def test_completion(self, model=MISTRAL_TEST_MODEL):
        prompt = ["This is a test"]
        kwargs = dict(model_name=model, prompt=prompt, temperature=0, seed=42)
        response = OpenAI(proxy_client=self.proxy_client).completions.create(**kwargs)
        self.assertIsInstance(response, Completion)
        response = OpenAI(proxy_client=self.proxy_client).with_raw_response.completions.create(**kwargs)
        self.assertIsInstance(response, openai._legacy_response.LegacyAPIResponse)

    def test_completion_global(self, model=MISTRAL_TEST_MODEL):
        from gen_ai_hub.proxy.native.openai import completions
        prompt = ["This is a test"]
        kwargs = dict(model_name=model, prompt=prompt, temperature=0, seed=42)
        response = completions.create(**kwargs)
        self.assertIsInstance(response, Completion)

    def test_structured_outputs(self, model=OPENAI_GPT_4O_MINI_TEST_MODEL):
        client = OpenAI(proxy_client=self.proxy_client, max_retries=10)
        response = client.chat.completions.parse(
            model=model,
            messages=[ChatCompletionUserMessageParam(role="user", content="Tell me about John Doe aged 30.")],
            response_format=Person
        )
        person = response.choices[0].message.parsed  # Fully typed Person object
        self.assertIsInstance(person, Person)
    
    @parameterized.expand(
        [
            OPENAI_GPT_4_1_MINI_TEST_MODEL,
            OPENAI_GPT_O4_MINI_TEST_MODEL,
            OPENAI_GPT_O3_MINI_TEST_MODEL,
            PERPLEXITY_TEST_MODEL,
        ]
    )
    def test_chat_completion_streaming(self, model=OPENAI_GPT_O3_MINI_TEST_MODEL):
        messages = self._get_test_messages()
        kwargs = {'model_name': model, 'messages': messages, 'stream': True, 'temperature': 0, 'seed': 42}
        generator = OpenAI(proxy_client=self.proxy_client, max_retries=10).chat.completions.create(**kwargs)
        self.assertIsInstance(generator, openai.Stream)
        chunks = [value for value in generator]
        self.assertTrue(all(isinstance(chunk, ChatCompletionChunk) for chunk in chunks))
        self.assertGreater(len(chunks), 1, 'Only one chunk received - stream seems to be buffered.')

    def test_structured_outputs_with_streaming(self, model=OPENAI_GPT_4O_MINI_TEST_MODEL):
        """
        streaming structured outputs requires the full object to be returned.
        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        client = OpenAI(proxy_client=self.proxy_client, max_retries=10)
        with client.chat.completions.with_streaming_response.parse(
            model=model,
            messages=[ChatCompletionUserMessageParam(role="user", content="Tell me about a person named John who is 30")],
            response_format=Person,
            temperature=0,
            seed=42,
        ) as stream:
            response = stream.parse()
            person = response.choices[0].message.parsed
            self.assertIsInstance(person, Person)

    def test_structured_outputs_with_beta_client_streaming(self, model=OPENAI_GPT_4O_MINI_TEST_MODEL):
        client = OpenAI(proxy_client=self.proxy_client, max_retries=10)
        with client.beta.chat.completions.stream(
            model=model,
            messages=[ChatCompletionUserMessageParam(role="user", content="Tell me about a person named John who is 30")],
            response_format=Person,
            temperature=0,
            seed=42,
        ) as stream:
            response = stream.get_final_completion() # This will wait for the full response to be received
            person = response.choices[0].message.parsed
            self.assertIsInstance(person, Person)

    @staticmethod
    def _get_test_messages():
        return [{
            'role': 'user',
            'content': 'Does Azure OpenAI support customer managed keys?'
        }, {
            'role': 'assistant',
            'content': 'Yes, customer managed keys are supported by Azure OpenAI.'
        }, {
            'role': 'user',
            'content': 'Do other Azure Cognitive Services support this too?'
        }]

    def test_cohere_command_a_reasoning(self, model=COHERE_COMMAND_A_TEST_MODEL):
        messages = self._get_test_messages()
        # Note: temperature should be automatically removed for reasoning models
        kwargs = dict(model_name=model, messages=messages, temperature=0.5, seed=42)
        response = OpenAI(proxy_client=self.proxy_client, max_retries=10).chat.completions.create(**kwargs)
        self.assertIsInstance(response, ChatCompletion)
        self.assertIsNotNone(response.model_extra['message']['content'][0])
        self.assertIsNotNone(response.model_extra['message']['content'][1])

    def test_cohere_rerank(self, model=COHERE_RERANK_TEST_MODEL):
        messages = self._get_test_messages()
        # Note: temperature should be automatically removed for reasoning models
        kwargs = dict(model_name=model, messages=messages, temperature=0.5, seed=42)
        response = OpenAI(proxy_client=self.proxy_client, max_retries=10).chat.completions.create(**kwargs)
        self.assertIsInstance(response, ChatCompletion)
        self.assertIsNotNone(response.model_extra['message']['content'][0])
        self.assertIsNotNone(response.model_extra['message']['content'][1])

    def test_function_calling(self):
        student_custom_functions = [
            {
                'name': 'extract_student_info',
                'description': 'Get the student information from the body of the input text',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'name': {
                            'type': 'string',
                            'description': 'Name of the person'
                        },
                        'major': {
                            'type': 'string',
                            'description': 'Major subject.'
                        },
                        'school': {
                            'type': 'string',
                            'description': 'The university name.'
                        }
                    }
                }
            }
        ]
        student_1_description = "David Nguyen is a sophomore majoring in computer science at Stanford University. He is Asian American and has a 3.8 GPA. David is known for his programming skills and is an active member of the university's Robotics Club. He hopes to pursue a career in artificial intelligence after graduating."

        kwargs = dict(
            model=OPENAI_GPT_O4_MINI_TEST_MODEL,
            messages=[{'role': 'user', 'content': student_1_description}],
            functions=student_custom_functions,
            function_call='auto',
            temperature=0,
            seed=42
        )
        response = OpenAI(proxy_client=self.proxy_client, max_retries=10).chat.completions.create(**kwargs)
        # Loading the response as a JSON object
        func_response = response.choices[0].message.function_call.arguments
        self.assertEqual(response.choices[0].finish_reason, 'function_call')
        self.assertEqual(response.choices[0].message.function_call.name, 'extract_student_info')
        import ast
        func_response_dict = ast.literal_eval(func_response)
        self.assertTrue(all(k in func_response for k in func_response_dict))


@unittest.skipIf(no_openai, 'openai not installed')
class AsyncOpenAITests(TestCaseAICoreSetupMixin, unittest.IsolatedAsyncioTestCase):

    async def test_async_embedding(self, model=OPENAI_EMBEDDING_TEST_MODEL):
        kwargs = {'input': 'Your text string goes here', 'model_name': model}
        response = await AsyncOpenAI(max_retries=10).embeddings.create(**kwargs)
        self.assertIsInstance(response, CreateEmbeddingResponse)
        response = await AsyncOpenAI(max_retries=10).with_raw_response.embeddings.create(**kwargs)
        self.assertIsInstance(response, openai._legacy_response.LegacyAPIResponse)

    async def test_async_nvidia_embedding(self, model=NVIDIA_EMBEDDING_TEST_MODEL):
        kwargs = {
            'input': 'Your text string goes here',
            'model_name': model,
            'extra_body': {'input_type': 'query'} # NVIDIA embedding model requires input_type
        }
        response = await AsyncOpenAI(max_retries=10).embeddings.create(**kwargs)
        self.assertIsInstance(response, CreateEmbeddingResponse)
        response = await AsyncOpenAI(max_retries=10).with_raw_response.embeddings.create(**kwargs)
        self.assertIsInstance(response, openai._legacy_response.LegacyAPIResponse)

    async def test_async_chat_completion(self, model=OPENAI_GPT_5_TEST_MODEL):
        prompt = 'Why is the sky blue?'
        kwargs = dict(model_name=model, messages=[{'role': 'user', 'content': prompt}], seed=42)
        response = await AsyncOpenAI(max_retries=10).chat.completions.create(**kwargs)
        self.assertIsInstance(response, ChatCompletion)
        response = await AsyncOpenAI(max_retries=10).with_raw_response.chat.completions.create(**kwargs)
        self.assertIsInstance(response, openai._legacy_response.LegacyAPIResponse)

    async def test_async_chat_completion_with_model_version_param(self, model=OPENAI_GPT_5_TEST_MODEL):
        prompt = 'Why is the sky blue?'
        kwargs = dict(model_name=model, messages=[{'role': 'user', 'content': prompt}], seed=42, model_version="latest")
        response = await AsyncOpenAI(max_retries=10).chat.completions.create(**kwargs)
        self.assertIsInstance(response, ChatCompletion)
        response = await AsyncOpenAI(max_retries=10).with_raw_response.chat.completions.create(**kwargs)
        self.assertIsInstance(response, openai._legacy_response.LegacyAPIResponse)

    @parameterized.expand(
        [
            OPENAI_GPT_O4_MINI_TEST_MODEL,
            PERPLEXITY_TEST_MODEL
        ]
    )
    async def test_async_chat_completion_streaming(self, model=OPENAI_GPT_O4_MINI_TEST_MODEL):
        messages = OpenAITests._get_test_messages()
        generator = await AsyncOpenAI(proxy_client=self.proxy_client, max_retries=10).chat.completions.create(
            model_name=model,
            messages=messages,
            stream=True)
        self.assertIsInstance(generator, openai.AsyncStream)
        chunks = [value async for value in generator]
        self.assertTrue(all(isinstance(chunk, ChatCompletionChunk) for chunk in chunks))
        self.assertGreater(len(chunks), 1, 'Only one chunk received - stream seems to be buffered.')

    async def test_async_completion(self, model=MISTRAL_TEST_MODEL):
        prompt = ["This is a test"]
        kwargs = dict(model_name=model, prompt=prompt, temperature=0, seed=42)
        response = await AsyncOpenAI(proxy_client=self.proxy_client).completions.create(**kwargs)
        self.assertIsInstance(response, Completion)
        response = await AsyncOpenAI(proxy_client=self.proxy_client).with_raw_response.completions.create(**kwargs)
        self.assertIsInstance(response, openai._legacy_response.LegacyAPIResponse)

    async def test_async_structured_outputs(self, model=OPENAI_GPT_4O_MINI_TEST_MODEL):
        client = AsyncOpenAI(proxy_client=self.proxy_client, max_retries=10)
        response = await client.chat.completions.parse(
            model=model,
            messages=[ChatCompletionUserMessageParam(role="user", content="Tell me about John Doe aged 30.")],
            response_format=Person
        )
        person = response.choices[0].message.parsed  # Fully typed Person object
        print(person)
        self.assertIsInstance(person, Person)

    async def test_async_structured_outputs_with_streaming(self, model=OPENAI_GPT_4O_MINI_TEST_MODEL):
        """
        streaming structured outputs requires the full object to be returned.
        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        client = AsyncOpenAI(proxy_client=self.proxy_client, max_retries=10)
        async with client.chat.completions.with_streaming_response.parse(
            model=model,
            messages=[{"role": "user", "content": "Tell me about a person named John who is 30"}],
            response_format=Person,
            temperature=0,
            seed=42,
        ) as stream:
            response = await stream.parse()
            person = response.choices[0].message.parsed
            self.assertIsInstance(person, Person)

    async def test_async_structured_outputs_with_beta_client_streaming(self, model=OPENAI_GPT_4O_MINI_TEST_MODEL):
        client = AsyncOpenAI(proxy_client=self.proxy_client, max_retries=10)
        async with client.beta.chat.completions.stream(
            model=model,
            messages=[{"role": "user", "content": "Tell me about a person named John who is 30"}],
            response_format=Person,
            temperature=0,
            seed=42,
        ) as stream:
            response = await stream.get_final_completion() # This will wait for the full response to be received
            person = response.choices[0].message.parsed
            self.assertIsInstance(person, Person)


if __name__ == '__main__':
    unittest.main()
