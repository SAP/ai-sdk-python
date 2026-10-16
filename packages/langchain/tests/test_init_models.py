import importlib
import importlib.util
import sys
import unittest
import unittest.mock
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from sap_ai_sdk_proxy.core.proxy_clients import get_proxy_client, proxy_version_context
from sap_ai_sdk_proxy.gen_ai_hub_proxy.client import Deployment
from sap_ai_sdk_langchain import openai
from sap_ai_sdk_langchain.init_models import (
    ModelType,
    init_embedding_model,
    init_llm,
)

# Provider adapters (amazon/google) live in their own packages; here we only
# exercise the openai path and the lazy dispatch to absent providers.
EMBEDDING_TEST_MODELS_TO_MODEL_CLASS_MAP = {
    "text-embedding-3-small": openai.OpenAIEmbeddings,
    "nvidia--llama-3.2-nv-embedqa-1b": openai.OpenAIEmbeddings
}

LLM_TEST_MODELS_MODEL_CLASS_MAP = {
    "gpt-5": openai.ChatOpenAI,
    "mistralai--mistral-small-instruct": openai.ChatOpenAI
}

TEST_MODELS = list(EMBEDDING_TEST_MODELS_TO_MODEL_CLASS_MAP.keys()) + list(LLM_TEST_MODELS_MODEL_CLASS_MAP.keys())


class TestInitModels(unittest.TestCase):

    @staticmethod
    def create_deployment(model_name: str):
        return Deployment(
            url=f'https://api.ai.internalprod.eu-central-1.aws.ml.hana.ondemand.com/v2/inference/deployments/{model_name}-url',
            deployment_id=f'{model_name}-deployment_id',
            config_name=f'{model_name}-config_name',
            config_id=f'{model_name}-config_id',
            model_name=model_name,
            model_version='latest',
            additonal_parameters={'model_type': str(ModelType.LLM)},
            created_at=datetime.now(),
        )

    @staticmethod
    def create_gen_ai_hub_deployments():
        deployments = []
        for model in TEST_MODELS:
            deployments.append(TestInitModels.create_deployment(model_name=model))
        return deployments

    @classmethod
    def setUpClass(cls) -> None:
        with proxy_version_context('gen-ai-hub'):
            cls.proxy_client = get_proxy_client(
                base_url='https://api.gen-ai.io',
                auth_url='https://auth.gen-ai.io',
                client_id='XXX',
                client_secret='XXX',
                resource_group='XXX'
            )
        cls.proxy_client._deployments = cls.create_gen_ai_hub_deployments()
        cls.proxy_client._get_scenario_deployments = MagicMock()
        cls.llm = LLM_TEST_MODELS_MODEL_CLASS_MAP
        cls.emb = EMBEDDING_TEST_MODELS_TO_MODEL_CLASS_MAP

    def setUp(self):
        self.proxy_client._get_scenario_deployments.reset_mock()

    def test_init_embedding_model(self):
        for model_name, model_class in self.emb.items():
            model = init_embedding_model(model_name, proxy_client=self.proxy_client)
            self.assertIsInstance(model, model_class)

    def test_init_llm_without_proxy_client(self):
        """init_llm should fall back to get_proxy_client() when proxy_client is not passed."""
        with unittest.mock.patch(
            'sap_ai_sdk_langchain.init_models.get_proxy_client',
            return_value=self.proxy_client,
        ):
            model = init_llm('gpt-5')
        self.assertIsInstance(model, openai.ChatOpenAI)

    def test_init_embedding_model_without_proxy_client(self):
        """init_embedding_model should fall back to get_proxy_client() when proxy_client is not passed."""
        with unittest.mock.patch(
            'sap_ai_sdk_langchain.init_models.get_proxy_client',
            return_value=self.proxy_client,
        ):
            model = init_embedding_model('text-embedding-3-small')
        self.assertIsInstance(model, openai.OpenAIEmbeddings)

    def test_init_llm(self):
        model_kwargs = {'top_k': 3}
        for model_name, model_class in self.llm.items():
            initiated_model = init_llm(model_name, proxy_client=self.proxy_client, **model_kwargs)
            self.assertIsInstance(initiated_model, model_class)

    def test_non_existing_model(self):
        with pytest.raises(ValueError):
            init_llm('michelangelo-1475', proxy_client=self.proxy_client)
        with pytest.raises(ValueError):
            init_embedding_model('michelangelo-1475', proxy_client=self.proxy_client)

    def test_custom_model(self):
        model_name = 'test-custom-model'
        init_func = openai.init_chat_model
        model_class = openai.ChatOpenAI
        custom_deployment = self.create_deployment(model_name)
        self.proxy_client._deployments.append(custom_deployment)
        model = init_llm(model_name, proxy_client=self.proxy_client, init_func=init_func)
        self.assertIsInstance(model, model_class)
        self.proxy_client._get_scenario_deployments.assert_not_called()

    def test_custom_embedding_model(self):
        model_name = 'test-custom-embed-model'
        init_func = openai.init_embedding_model
        model_class = openai.OpenAIEmbeddings
        custom_deployment = self.create_deployment(model_name)
        self.proxy_client._deployments.append(custom_deployment)
        model = init_embedding_model(model_name, proxy_client=self.proxy_client, init_func=init_func)
        self.assertIsInstance(model, model_class)
        self.proxy_client._get_scenario_deployments.assert_not_called()

    def test_update_deployments_called_for_custom_model(self):
        model_name = 'test-custom-model'
        init_func = openai.init_chat_model
        model_class = openai.ChatOpenAI
        custom_deployment = self.create_deployment(model_name)
        deployments = self.create_gen_ai_hub_deployments()
        deployments.append(custom_deployment)
        deployments_dict = {}
        for i in range(len(deployments)):
            deployments_dict[i] = deployments[i]
        self.proxy_client._get_scenario_deployments.return_value = deployments_dict
        model = init_llm(model_name, proxy_client=self.proxy_client, init_func=init_func)
        self.assertIsInstance(model, model_class)
        self.proxy_client._get_scenario_deployments.assert_called_once_with(
            self.proxy_client.foundational_model_scenarios[0])

    def test_custom_model_fails_if_deployment_does_not_exist(self):
        model_name = 'not-existing-model'
        init_func = openai.init_chat_model
        deployments = self.create_gen_ai_hub_deployments()
        deployments_dict = {}
        for i in range(len(deployments)):
            deployments_dict[i] = deployments[i]
        self.proxy_client._get_scenario_deployments.return_value = deployments_dict

        with self.assertRaises(ValueError) as cm:
            init_llm(model_name, proxy_client=self.proxy_client, init_func=init_func)
        self.assertIn('No deployment found', cm.exception.args[0])
        self.assertIn(model_name, cm.exception.args[0])


class TestLazyProviderDispatch(unittest.TestCase):
    """The provider adapters (amazon/google) live in separate packages and are
    imported lazily. When the provider package is not installed, dispatching to
    it must raise an actionable ImportError naming the pip install command."""

    def _assert_actionable_import_error(self, model_name: str, provider_module: str, distribution: str):
        proxy_client = MagicMock()
        proxy_client.deployment_class.get_main_model_identification_kwargs.return_value = 'model_name'
        proxy_client.deployment_class.get_model_identification_kwargs.return_value = ['model_name']

        # Simulate the provider package being absent.
        with unittest.mock.patch.dict(sys.modules, {f'{provider_module}.langchain': None}):
            # Drop any cached import so the patched (missing) module is seen.
            sys.modules.pop(f'{provider_module}.langchain', None)
            with self.assertRaises(ImportError) as cm:
                init_llm(model_name, proxy_client=proxy_client)
        message = str(cm.exception)
        self.assertIn(distribution, message)
        self.assertIn('[langchain]', message)

    def test_amazon_dispatch_raises_actionable_error_when_absent(self):
        if importlib.util.find_spec('sap_ai_sdk_amazon') is not None:
            self.skipTest('sap-ai-sdk-amazon is installed; lazy-error path not exercised')
        self._assert_actionable_import_error('amazon--nova-micro', 'sap_ai_sdk_amazon', 'sap-ai-sdk-amazon')

    def test_google_dispatch_raises_actionable_error_when_absent(self):
        if importlib.util.find_spec('sap_ai_sdk_google') is not None:
            self.skipTest('sap-ai-sdk-google is installed; lazy-error path not exercised')
        self._assert_actionable_import_error('gemini-2.5-flash-lite', 'sap_ai_sdk_google', 'sap-ai-sdk-google')
