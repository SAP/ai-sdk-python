import unittest
from typing import Callable

from langchain_classic.chains import LLMChain
from langchain_classic.prompts import PromptTemplate

from gen_ai_hub.proxy.langchain.init_models import ModelType, init_embedding_model, init_llm, _get_init_func
from integration_tests.constants import (OPENAI_GPT_4O_MINI_TEST_MODEL,
                                         AMAZON_TITAN_EMBEDDING_TEST_MODEL, OPENAI_EMBEDDING_TEST_MODEL,
                                         GEMINI_2_5_FLASH_LITE_TEST_MODEL)
from integration_tests.setup_aicore import TestCaseAICoreSetupMixin


class TestInitModels(TestCaseAICoreSetupMixin, unittest.TestCase):

    def test_init_llm(self):
        template = """Question: {question}
        Answer: Let's think step by step."""
        prompt = PromptTemplate(template=template, input_variables=['question'])
        question = 'What is a supernova?'
        models=[GEMINI_2_5_FLASH_LITE_TEST_MODEL, OPENAI_GPT_4O_MINI_TEST_MODEL]  # CLAUDE_3_7_SONNET_TEST_MODEL
        for model in models:
            try:
                self.proxy_client.select_deployment(model_name=model)
            except ValueError:
                # skip if deployment is not available
                continue
            llm = init_llm(model, max_tokens=24, proxy_client=self.proxy_client)
            llm_chain = LLMChain(prompt=prompt, llm=llm)
            answer = llm_chain.invoke(question)
            self.assertIsInstance(answer['text'], str)

    def _do_test_custom_models(self, models: list, model_type: ModelType, init_model: Callable):
        question = 'What is a supernova?'
        for model_name in models:
            try:
                self.proxy_client.select_deployment(model_name=model_name)
            except ValueError:
                # skip if deployment is not available
                continue

            init_func = _get_init_func(model_name, model_type)
            model = init_model(model_name, max_tokens=24, proxy_client=self.proxy_client, init_func=init_func)
            if model_type == ModelType.EMBEDDINGS:
                response = model.embed_query(question)
                self.assertIsInstance(response, list)
                self.assertTrue(all(isinstance(item, float) for item in response))
            else:
                answer = model.invoke(question)
                self.assertTrue(len(str(answer)) > 0, msg=f"Model {model_name} failed to generate a response")

    def test_init_custom_model(self):
        """
        Test custom models that are not in the catalog.
        Therefor, we delete the model entry from the catalog and test the model initialization.
        Only one model per model provider is tested.
        """
        self._do_test_custom_models(models=[GEMINI_2_5_FLASH_LITE_TEST_MODEL, OPENAI_GPT_4O_MINI_TEST_MODEL],  # CLAUDE_3_7_SONNET_TEST_MODEL
                                    model_type=ModelType.LLM,
                                    init_model=init_llm)

        # test custom embedding models
        self._do_test_custom_models(models=[AMAZON_TITAN_EMBEDDING_TEST_MODEL, OPENAI_EMBEDDING_TEST_MODEL],
                                    model_type=ModelType.EMBEDDINGS,
                                    init_model=init_embedding_model)

    def test_init_embedding_model(self):
        text = 'What is a supernova?'
        for model in [AMAZON_TITAN_EMBEDDING_TEST_MODEL, OPENAI_EMBEDDING_TEST_MODEL]:
            try:
                self.proxy_client.select_deployment(model_name=model)
            except ValueError:
                # skip if deployment is not available
                continue
            emb = init_embedding_model(model, proxy_client=self.proxy_client)
            response = emb.embed_query(text)
            self.assertIsInstance(response, list)
            self.assertTrue(all(isinstance(item, float) for item in response))
