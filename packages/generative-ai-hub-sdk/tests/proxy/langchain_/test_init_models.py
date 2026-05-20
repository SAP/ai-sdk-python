import unittest
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client, proxy_version_context
from gen_ai_hub.proxy.gen_ai_hub_proxy.client import Deployment
from gen_ai_hub.proxy.langchain import amazon, google_genai
from gen_ai_hub.proxy.langchain.init_models import (
    ModelType,
    catalog,
    get_model_class,
    init_embedding_model,
    init_llm,
)


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
        for model_type, models in catalog.models['gen-ai-hub'].items():
            for model in models.keys():
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
        cls.llm = catalog.models['gen-ai-hub'][ModelType.LLM]
        cls.emb = catalog.models['gen-ai-hub'][ModelType.EMBEDDINGS]

    def setUp(self):
        self.proxy_client._get_scenario_deployments.reset_mock()

    def test_init_embedding_model(self):
        for model, entry in self.emb.items():
            model = init_embedding_model(model, proxy_client=self.proxy_client)
            self.assertIsInstance(model, entry.model)

    def test_init_llm(self):
        model_kwargs = {'top_k': 3}
        for model, entry in self.llm.items():
            model = init_llm(model, proxy_client=self.proxy_client, **model_kwargs)
            self.assertIsInstance(model, entry.model)

    def test_get_model_class(self):
        for model, entry in self.llm.items():
            model_cls = get_model_class(model, proxy_client=self.proxy_client)
            self.assertEqual(model_cls, entry.model)

    def test_non_existing_model(self):
        with pytest.raises(KeyError):
            init_llm('michelangelo-1475', proxy_client=self.proxy_client)
        with pytest.raises(KeyError):
            init_embedding_model('michelangelo-1475', proxy_client=self.proxy_client)

    def test_custom_model(self):
        model_name = 'test-custom-model'
        init_func = google_genai.init_chat_model
        model_class = google_genai.ChatGoogleGenerativeAI
        custom_deployment = self.create_deployment(model_name)
        self.proxy_client._deployments.append(custom_deployment)
        model = init_llm(model_name, proxy_client=self.proxy_client, init_func=init_func)
        self.assertIsInstance(model, model_class)
        self.proxy_client._get_scenario_deployments.assert_not_called()

    def test_custom_amazon_model(self):
        model_name = 'test-custom-amazon-model'
        model_id = f'{model_name}-id'
        init_func = amazon.init_chat_model
        model_class = amazon.ChatBedrock
        custom_deployment = self.create_deployment(model_name)
        self.proxy_client._deployments.append(custom_deployment)
        model = init_llm(model_name, model_id=model_id, proxy_client=self.proxy_client, init_func=init_func)
        self.assertIsInstance(model, model_class)
        self.proxy_client._get_scenario_deployments.assert_not_called()

    def test_custom_amazon_embedding_model(self):
        model_name = 'test-custom-embed-model'
        model_id = f'{model_name}-id'
        init_func = amazon.init_embedding_model
        model_class = amazon.BedrockEmbeddings
        custom_deployment = self.create_deployment(model_name)
        self.proxy_client._deployments.append(custom_deployment)
        model = init_embedding_model(model_name, model_id=model_id, proxy_client=self.proxy_client, init_func=init_func)
        self.assertIsInstance(model, model_class)
        self.proxy_client._get_scenario_deployments.assert_not_called()

    def test_update_deployments_called_for_custom_model(self):
        model_name = 'test-custom-model'
        init_func = google_genai.init_chat_model
        model_class = google_genai.ChatGoogleGenerativeAI
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
        init_func = google_genai.init_chat_model
        model_class = google_genai.ChatGoogleGenerativeAI
        deployments = self.create_gen_ai_hub_deployments()
        deployments_dict = {}
        for i in range(len(deployments)):
            deployments_dict[i] = deployments[i]
        self.proxy_client._get_scenario_deployments.return_value = deployments_dict

        with self.assertRaises(ValueError) as cm:
            init_llm(model_name, proxy_client=self.proxy_client, init_func=init_func)
        self.assertIn('No deployment found', cm.exception.args[0])
        self.assertIn(model_name, cm.exception.args[0])
