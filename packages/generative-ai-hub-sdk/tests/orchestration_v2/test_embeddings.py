import unittest

from gen_ai_hub.orchestration_v2.models.embeddings import (
    EmbeddingsEncodingFormat,
    EmbeddingsInputType,
    EmbeddingsModelParams,
    EmbeddingsModelDetails,
    EmbeddingsModelConfig,
    EmbeddingsModuleConfigs,
    EmbeddingsOrchestrationConfig,
    EmbeddingsInput,
    EmbeddingsUsage,
    EmbeddingResult,
    EmbeddingsResponse,
    EmbeddingsPostResponse,
    EmbeddingsRequest,
)
from gen_ai_hub.orchestration_v2.models.data_masking import (
    MaskingModuleConfig,
    MaskingProviderConfig,
    MaskingMethod,
    DPIStandardEntity,
    ProfileEntity,
)


class TestEmbeddingsEnums(unittest.TestCase):
    """Tests for embedding-related enums."""

    def test_encoding_format_values(self):
        self.assertEqual(EmbeddingsEncodingFormat.FLOAT.value, "float")
        self.assertEqual(EmbeddingsEncodingFormat.BASE64.value, "base64")
        self.assertEqual(EmbeddingsEncodingFormat.BINARY.value, "binary")

    def test_input_type_values(self):
        self.assertEqual(EmbeddingsInputType.TEXT.value, "text")
        self.assertEqual(EmbeddingsInputType.DOCUMENT.value, "document")
        self.assertEqual(EmbeddingsInputType.QUERY.value, "query")


class TestEmbeddingsModelParams(unittest.TestCase):
    """Tests for EmbeddingsModelParams model."""

    def test_empty_params(self):
        params = EmbeddingsModelParams()
        self.assertIsNone(params.dimensions)
        self.assertIsNone(params.encoding_format)
        self.assertIsNone(params.normalize)
        self.assertEqual(params.model_dump(), {})

    def test_params_with_dimensions(self):
        params = EmbeddingsModelParams(dimensions=256)
        self.assertEqual(params.dimensions, 256)
        self.assertEqual(params.model_dump(), {"dimensions": 256})

    def test_params_with_encoding_format(self):
        params = EmbeddingsModelParams(encoding_format=EmbeddingsEncodingFormat.BASE64)
        self.assertEqual(params.encoding_format, EmbeddingsEncodingFormat.BASE64)
        self.assertEqual(params.model_dump(), {"encoding_format": "base64"})

    def test_params_with_normalize(self):
        params = EmbeddingsModelParams(normalize=True)
        self.assertTrue(params.normalize)
        self.assertEqual(params.model_dump(), {"normalize": True})

    def test_full_params(self):
        params = EmbeddingsModelParams(
            dimensions=1536,
            encoding_format=EmbeddingsEncodingFormat.FLOAT,
            normalize=True
        )
        expected = {
            "dimensions": 1536,
            "encoding_format": "float",
            "normalize": True
        }
        self.assertEqual(params.model_dump(), expected)


class TestEmbeddingsModelDetails(unittest.TestCase):
    """Tests for EmbeddingsModelDetails model."""

    def test_minimal_model_details(self):
        details = EmbeddingsModelDetails(name="text-embedding-3-large")
        self.assertEqual(details.name, "text-embedding-3-large")
        self.assertEqual(details.version, "latest")
        self.assertIsNone(details.params)
        self.assertEqual(details.timeout, 600)
        self.assertEqual(details.max_retries, 2)

    def test_model_details_with_version(self):
        details = EmbeddingsModelDetails(name="text-embedding-3-large", version="2024-01")
        self.assertEqual(details.version, "2024-01")

    def test_model_details_with_params(self):
        params = EmbeddingsModelParams(dimensions=512)
        details = EmbeddingsModelDetails(
            name="text-embedding-3-large",
            params=params
        )
        self.assertEqual(details.params.dimensions, 512)

    def test_model_details_with_custom_timeout(self):
        details = EmbeddingsModelDetails(name="test-model", timeout=300)
        self.assertEqual(details.timeout, 300)

    def test_model_details_with_custom_max_retries(self):
        details = EmbeddingsModelDetails(name="test-model", max_retries=5)
        self.assertEqual(details.max_retries, 5)

    def test_model_details_dump(self):
        params = EmbeddingsModelParams(dimensions=256, normalize=True)
        details = EmbeddingsModelDetails(
            name="text-embedding-3-small",
            version="latest",
            params=params,
            timeout=120,
            max_retries=3
        )
        expected = {
            "name": "text-embedding-3-small",
            "version": "latest",
            "params": {
                "dimensions": 256,
                "normalize": True
            },
            "timeout": 120,
            "max_retries": 3
        }
        self.assertEqual(details.model_dump(), expected)


class TestEmbeddingsModelConfig(unittest.TestCase):
    """Tests for EmbeddingsModelConfig model."""

    def test_embeddings_model_config(self):
        model_details = EmbeddingsModelDetails(name="text-embedding-3-large")
        config = EmbeddingsModelConfig(model=model_details)
        self.assertEqual(config.model.name, "text-embedding-3-large")

    def test_embeddings_model_config_dump(self):
        model_details = EmbeddingsModelDetails(name="text-embedding-ada-002")
        config = EmbeddingsModelConfig(model=model_details)
        result = config.model_dump()
        self.assertIn("model", result)
        self.assertEqual(result["model"]["name"], "text-embedding-ada-002")


class TestEmbeddingsModuleConfigs(unittest.TestCase):
    """Tests for EmbeddingsModuleConfigs model."""

    def test_minimal_module_configs(self):
        embeddings_config = EmbeddingsModelConfig(
            model=EmbeddingsModelDetails(name="text-embedding-3-large")
        )
        modules = EmbeddingsModuleConfigs(embeddings=embeddings_config)
        self.assertIsNotNone(modules.embeddings)
        self.assertIsNone(modules.masking)

    def test_module_configs_with_masking(self):
        embeddings_config = EmbeddingsModelConfig(
            model=EmbeddingsModelDetails(name="text-embedding-3-large")
        )
        masking_config = MaskingModuleConfig(
            masking_providers=[
                MaskingProviderConfig(
                    method=MaskingMethod.ANONYMIZATION,
                    entities=[DPIStandardEntity(type=ProfileEntity.EMAIL)]
                )
            ]
        )
        modules = EmbeddingsModuleConfigs(
            embeddings=embeddings_config,
            masking=masking_config
        )
        self.assertIsNotNone(modules.embeddings)
        self.assertIsNotNone(modules.masking)

    def test_module_configs_dump(self):
        embeddings_config = EmbeddingsModelConfig(
            model=EmbeddingsModelDetails(name="text-embedding-3-large")
        )
        modules = EmbeddingsModuleConfigs(embeddings=embeddings_config)
        result = modules.model_dump()
        self.assertIn("embeddings", result)
        self.assertEqual(result["embeddings"]["model"]["name"], "text-embedding-3-large")


class TestEmbeddingsOrchestrationConfig(unittest.TestCase):
    """Tests for EmbeddingsOrchestrationConfig model."""

    def test_orchestration_config(self):
        modules = EmbeddingsModuleConfigs(
            embeddings=EmbeddingsModelConfig(
                model=EmbeddingsModelDetails(name="text-embedding-3-large")
            )
        )
        config = EmbeddingsOrchestrationConfig(modules=modules)
        self.assertEqual(config.modules.embeddings.model.name, "text-embedding-3-large")

    def test_orchestration_config_dump(self):
        modules = EmbeddingsModuleConfigs(
            embeddings=EmbeddingsModelConfig(
                model=EmbeddingsModelDetails(
                    name="text-embedding-3-large",
                    params=EmbeddingsModelParams(dimensions=256)
                )
            )
        )
        config = EmbeddingsOrchestrationConfig(modules=modules)
        result = config.model_dump()
        self.assertIn("modules", result)
        self.assertEqual(result["modules"]["embeddings"]["model"]["params"]["dimensions"], 256)


class TestEmbeddingsInput(unittest.TestCase):
    """Tests for EmbeddingsInput model."""

    def test_single_text_input(self):
        input_obj = EmbeddingsInput(text="Hello, World!")
        self.assertEqual(input_obj.text, "Hello, World!")
        self.assertIsNone(input_obj.type_)

    def test_list_text_input(self):
        texts = ["Hello", "World", "Test"]
        input_obj = EmbeddingsInput(text=texts)
        self.assertEqual(input_obj.text, texts)
        self.assertEqual(len(input_obj.text), 3)

    def test_input_with_type_text(self):
        input_obj = EmbeddingsInput(text="Test", type=EmbeddingsInputType.TEXT)
        self.assertEqual(input_obj.type_, EmbeddingsInputType.TEXT)

    def test_input_with_type_document(self):
        input_obj = EmbeddingsInput(text="Document content", type=EmbeddingsInputType.DOCUMENT)
        self.assertEqual(input_obj.type_, EmbeddingsInputType.DOCUMENT)

    def test_input_with_type_query(self):
        input_obj = EmbeddingsInput(text="Search query?", type=EmbeddingsInputType.QUERY)
        self.assertEqual(input_obj.type_, EmbeddingsInputType.QUERY)

    def test_input_dump_single_text(self):
        input_obj = EmbeddingsInput(text="Hello")
        result = input_obj.model_dump()
        self.assertEqual(result, {"text": "Hello"})

    def test_input_dump_with_type(self):
        input_obj = EmbeddingsInput(text="Query", type=EmbeddingsInputType.QUERY)
        result = input_obj.model_dump()
        self.assertEqual(result, {"text": "Query", "type": "query"})

    def test_input_dump_list(self):
        input_obj = EmbeddingsInput(text=["a", "b", "c"])
        result = input_obj.model_dump()
        self.assertEqual(result, {"text": ["a", "b", "c"]})


class TestEmbeddingsUsage(unittest.TestCase):
    """Tests for EmbeddingsUsage model."""

    def test_usage(self):
        usage = EmbeddingsUsage(prompt_tokens=10, total_tokens=10)
        self.assertEqual(usage.prompt_tokens, 10)
        self.assertEqual(usage.total_tokens, 10)

    def test_usage_dump(self):
        usage = EmbeddingsUsage(prompt_tokens=100, total_tokens=100)
        result = usage.model_dump()
        self.assertEqual(result, {"prompt_tokens": 100, "total_tokens": 100})


class TestEmbeddingResult(unittest.TestCase):
    """Tests for EmbeddingResult model."""

    def test_embedding_result_with_float_list(self):
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        result = EmbeddingResult(object="embedding", embedding=embedding, index=0)
        self.assertEqual(result.object, "embedding")
        self.assertEqual(result.embedding, embedding)
        self.assertEqual(result.index, 0)

    def test_embedding_result_with_base64_string(self):
        base64_embedding = "SGVsbG8gV29ybGQ="
        result = EmbeddingResult(object="embedding", embedding=base64_embedding, index=1)
        self.assertEqual(result.embedding, base64_embedding)
        self.assertEqual(result.index, 1)

    def test_embedding_result_dump(self):
        result = EmbeddingResult(
            object="embedding",
            embedding=[0.1, 0.2, 0.3],
            index=0
        )
        dumped = result.model_dump()
        self.assertEqual(dumped["object"], "embedding")
        self.assertEqual(dumped["embedding"], [0.1, 0.2, 0.3])
        self.assertEqual(dumped["index"], 0)


class TestEmbeddingsResponse(unittest.TestCase):
    """Tests for EmbeddingsResponse model."""

    def test_embeddings_response(self):
        data = [
            EmbeddingResult(object="embedding", embedding=[0.1, 0.2], index=0),
            EmbeddingResult(object="embedding", embedding=[0.3, 0.4], index=1),
        ]
        usage = EmbeddingsUsage(prompt_tokens=10, total_tokens=10)
        response = EmbeddingsResponse(
            object="list",
            data=data,
            model="text-embedding-3-large",
            usage=usage
        )
        self.assertEqual(response.object, "list")
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.model, "text-embedding-3-large")
        self.assertEqual(response.usage.prompt_tokens, 10)

    def test_embeddings_response_dump(self):
        data = [EmbeddingResult(object="embedding", embedding=[0.1], index=0)]
        usage = EmbeddingsUsage(prompt_tokens=5, total_tokens=5)
        response = EmbeddingsResponse(
            object="list",
            data=data,
            model="test-model",
            usage=usage
        )
        result = response.model_dump()
        self.assertEqual(result["object"], "list")
        self.assertEqual(result["model"], "test-model")
        self.assertIn("data", result)
        self.assertIn("usage", result)


class TestEmbeddingsPostResponse(unittest.TestCase):
    """Tests for EmbeddingsPostResponse model."""

    def test_post_response_minimal(self):
        final_result = EmbeddingsResponse(
            object="list",
            data=[EmbeddingResult(object="embedding", embedding=[0.1, 0.2], index=0)],
            model="text-embedding-3-large",
            usage=EmbeddingsUsage(prompt_tokens=5, total_tokens=5)
        )
        response = EmbeddingsPostResponse(
            request_id="test-123",
            final_result=final_result
        )
        self.assertEqual(response.request_id, "test-123")
        self.assertIsNone(response.intermediate_results)
        self.assertEqual(response.final_result.model, "text-embedding-3-large")

    def test_post_response_with_intermediate_results(self):
        final_result = EmbeddingsResponse(
            object="list",
            data=[EmbeddingResult(object="embedding", embedding=[0.1], index=0)],
            model="text-embedding-3-large",
            usage=EmbeddingsUsage(prompt_tokens=5, total_tokens=5)
        )
        intermediate = {
            "input_masking": {
                "message": "Embedding input is masked successfully.",
                "data": {"masked_input": "Contact MASKED_PERSON at MASKED_EMAIL"}
            }
        }
        response = EmbeddingsPostResponse(
            request_id="test-456",
            intermediate_results=intermediate,
            final_result=final_result
        )
        self.assertEqual(response.request_id, "test-456")
        self.assertIsNotNone(response.intermediate_results)
        self.assertIn("input_masking", response.intermediate_results)

    def test_post_response_dump(self):
        final_result = EmbeddingsResponse(
            object="list",
            data=[EmbeddingResult(object="embedding", embedding=[0.5], index=0)],
            model="test-model",
            usage=EmbeddingsUsage(prompt_tokens=1, total_tokens=1)
        )
        response = EmbeddingsPostResponse(
            request_id="dump-test",
            final_result=final_result
        )
        result = response.model_dump()
        self.assertEqual(result["request_id"], "dump-test")
        self.assertIn("final_result", result)


class TestEmbeddingsRequest(unittest.TestCase):
    """Tests for EmbeddingsRequest model."""

    def test_embeddings_request(self):
        config = EmbeddingsOrchestrationConfig(
            modules=EmbeddingsModuleConfigs(
                embeddings=EmbeddingsModelConfig(
                    model=EmbeddingsModelDetails(name="text-embedding-3-large")
                )
            )
        )
        input_obj = EmbeddingsInput(text="Hello World")
        request = EmbeddingsRequest(config=config, input=input_obj)
        self.assertEqual(request.config.modules.embeddings.model.name, "text-embedding-3-large")
        self.assertEqual(request.input.text, "Hello World")

    def test_embeddings_request_dump(self):
        config = EmbeddingsOrchestrationConfig(
            modules=EmbeddingsModuleConfigs(
                embeddings=EmbeddingsModelConfig(
                    model=EmbeddingsModelDetails(
                        name="text-embedding-3-large",
                        params=EmbeddingsModelParams(dimensions=256)
                    )
                )
            )
        )
        input_obj = EmbeddingsInput(text=["text1", "text2"], type=EmbeddingsInputType.DOCUMENT)
        request = EmbeddingsRequest(config=config, input=input_obj)
        result = request.model_dump()

        self.assertIn("config", result)
        self.assertIn("input", result)
        self.assertEqual(result["config"]["modules"]["embeddings"]["model"]["name"], "text-embedding-3-large")
        self.assertEqual(result["config"]["modules"]["embeddings"]["model"]["params"]["dimensions"], 256)
        self.assertEqual(result["input"]["text"], ["text1", "text2"])
        self.assertEqual(result["input"]["type"], "document")


class TestEmbeddingsServiceSync(unittest.TestCase):
    """Tests for OrchestrationService embed method (sync)."""

    def setUp(self):
        from tests.mock import get_mocked_ai_core_client, ai_core_ai_api_mocker
        self.api_url = "https://api.example.com"
        self.proxy_client = get_mocked_ai_core_client(client_id='testembeddingsclient')
        self.ai_core_mocker = ai_core_ai_api_mocker

        self.embeddings_config = EmbeddingsOrchestrationConfig(
            modules=EmbeddingsModuleConfigs(
                embeddings=EmbeddingsModelConfig(
                    model=EmbeddingsModelDetails(name="text-embedding-3-large")
                )
            )
        )
        self.embeddings_input = EmbeddingsInput(text="Hello World!")

    def test_embed_single_text(self):
        from gen_ai_hub.orchestration_v2.service import OrchestrationService
        from tests.mock import orchestration_embeddings_v2_mocker

        with self.ai_core_mocker(auth_url=self.proxy_client.auth_url, base_url=self.proxy_client.base_url):
            service = OrchestrationService(api_url=self.api_url, proxy_client=self.proxy_client)
            with orchestration_embeddings_v2_mocker(service.api_url + '/v2/embeddings'):
                response = service.embed(config=self.embeddings_config, input=self.embeddings_input)

                self.assertIsInstance(response, EmbeddingsPostResponse)
                self.assertEqual(response.request_id, "emb-test-123")
                self.assertEqual(response.final_result.model, "text-embedding-3-large")
                self.assertEqual(len(response.final_result.data), 1)
                self.assertEqual(response.final_result.data[0].index, 0)
                self.assertEqual(len(response.final_result.data[0].embedding), 3072)

    def test_embed_batch_texts(self):
        from gen_ai_hub.orchestration_v2.service import OrchestrationService
        from tests.mock import orchestration_embeddings_v2_batch_mocker

        batch_input = EmbeddingsInput(text=["Text 1", "Text 2", "Text 3"])

        with self.ai_core_mocker(auth_url=self.proxy_client.auth_url, base_url=self.proxy_client.base_url):
            service = OrchestrationService(api_url=self.api_url, proxy_client=self.proxy_client)
            with orchestration_embeddings_v2_batch_mocker(service.api_url + '/v2/embeddings'):
                response = service.embed(config=self.embeddings_config, input=batch_input)

                self.assertEqual(len(response.final_result.data), 3)
                for i, result in enumerate(response.final_result.data):
                    self.assertEqual(result.index, i)
                    self.assertEqual(len(result.embedding), 256)

    def test_embed_with_masking(self):
        from gen_ai_hub.orchestration_v2.service import OrchestrationService
        from tests.mock import orchestration_embeddings_v2_with_masking_mocker

        config_with_masking = EmbeddingsOrchestrationConfig(
            modules=EmbeddingsModuleConfigs(
                embeddings=EmbeddingsModelConfig(
                    model=EmbeddingsModelDetails(name="text-embedding-3-large")
                ),
                masking=MaskingModuleConfig(
                    masking_providers=[
                        MaskingProviderConfig(
                            method=MaskingMethod.ANONYMIZATION,
                            entities=[
                                DPIStandardEntity(type=ProfileEntity.PERSON),
                                DPIStandardEntity(type=ProfileEntity.EMAIL),
                            ]
                        )
                    ]
                )
            )
        )
        masked_input = EmbeddingsInput(text="Contact John at john@example.com")

        with self.ai_core_mocker(auth_url=self.proxy_client.auth_url, base_url=self.proxy_client.base_url):
            service = OrchestrationService(api_url=self.api_url, proxy_client=self.proxy_client)
            with orchestration_embeddings_v2_with_masking_mocker(service.api_url + '/v2/embeddings'):
                response = service.embed(config=config_with_masking, input=masked_input)

                self.assertIsNotNone(response.intermediate_results)
                self.assertIn("input_masking", response.intermediate_results)
                self.assertIn("MASKED_PERSON", response.intermediate_results["input_masking"]["data"]["masked_input"])

    def test_embed_with_custom_params(self):
        from gen_ai_hub.orchestration_v2.service import OrchestrationService
        from tests.mock import orchestration_embeddings_v2_mocker

        config_with_params = EmbeddingsOrchestrationConfig(
            modules=EmbeddingsModuleConfigs(
                embeddings=EmbeddingsModelConfig(
                    model=EmbeddingsModelDetails(
                        name="text-embedding-3-large",
                        params=EmbeddingsModelParams(
                            dimensions=256,
                            encoding_format=EmbeddingsEncodingFormat.FLOAT,
                            normalize=True
                        )
                    )
                )
            )
        )

        with self.ai_core_mocker(auth_url=self.proxy_client.auth_url, base_url=self.proxy_client.base_url):
            service = OrchestrationService(api_url=self.api_url, proxy_client=self.proxy_client)
            with orchestration_embeddings_v2_mocker(service.api_url + '/v2/embeddings'):
                response = service.embed(config=config_with_params, input=self.embeddings_input)
                self.assertIsInstance(response, EmbeddingsPostResponse)

    def test_embed_with_input_type(self):
        from gen_ai_hub.orchestration_v2.service import OrchestrationService
        from tests.mock import orchestration_embeddings_v2_mocker

        doc_input = EmbeddingsInput(text="Document content", type=EmbeddingsInputType.DOCUMENT)
        query_input = EmbeddingsInput(text="Search query", type=EmbeddingsInputType.QUERY)

        with self.ai_core_mocker(auth_url=self.proxy_client.auth_url, base_url=self.proxy_client.base_url):
            service = OrchestrationService(api_url=self.api_url, proxy_client=self.proxy_client)
            with orchestration_embeddings_v2_mocker(service.api_url + '/v2/embeddings'):
                # Test document type
                response = service.embed(config=self.embeddings_config, input=doc_input)
                self.assertIsInstance(response, EmbeddingsPostResponse)

                # Test query type
                response = service.embed(config=self.embeddings_config, input=query_input)
                self.assertIsInstance(response, EmbeddingsPostResponse)

    def test_embed_timeout_parameter(self):
        from gen_ai_hub.orchestration_v2.service import OrchestrationService
        from tests.mock import GET_ORCHESTRATION_V2_EMBEDDINGS_RESPONSE
        from unittest.mock import patch

        class FakeResponse:
            def raise_for_status(self):
                pass

            def json(self):
                return GET_ORCHESTRATION_V2_EMBEDDINGS_RESPONSE

        timeout_captured = {}

        def capture_request(*args, **kwargs):
            nonlocal timeout_captured
            timeout_captured = kwargs
            return FakeResponse()

        with self.ai_core_mocker(auth_url=self.proxy_client.auth_url, base_url=self.proxy_client.base_url):
            service = OrchestrationService(api_url=self.api_url, proxy_client=self.proxy_client)
            with patch.object(service.client, "post", side_effect=capture_request):
                service.embed(config=self.embeddings_config, input=self.embeddings_input, timeout=120.0)
            self.assertEqual(timeout_captured.get("timeout"), 120.0)


class TestEmbeddingsServiceAsync(unittest.IsolatedAsyncioTestCase):
    """Tests for OrchestrationService aembed method (async)."""

    def setUp(self):
        from tests.mock import get_mocked_ai_core_client, ai_core_ai_api_mocker
        self.api_url = "https://api.example.com"
        self.proxy_client = get_mocked_ai_core_client(client_id='testembeddingsasyncclient')
        self.ai_core_mocker = ai_core_ai_api_mocker

        self.embeddings_config = EmbeddingsOrchestrationConfig(
            modules=EmbeddingsModuleConfigs(
                embeddings=EmbeddingsModelConfig(
                    model=EmbeddingsModelDetails(name="text-embedding-3-large")
                )
            )
        )
        self.embeddings_input = EmbeddingsInput(text="Hello World!")

    async def test_aembed_single_text(self):
        from gen_ai_hub.orchestration_v2.service import OrchestrationService
        from tests.mock import orchestration_embeddings_v2_mocker

        with self.ai_core_mocker(auth_url=self.proxy_client.auth_url, base_url=self.proxy_client.base_url):
            service = OrchestrationService(api_url=self.api_url, proxy_client=self.proxy_client)
            with orchestration_embeddings_v2_mocker(service.api_url + '/v2/embeddings'):
                response = await service.aembed(config=self.embeddings_config, input=self.embeddings_input)

                self.assertIsInstance(response, EmbeddingsPostResponse)
                self.assertEqual(response.request_id, "emb-test-123")
                self.assertEqual(response.final_result.model, "text-embedding-3-large")

    async def test_aembed_batch_texts(self):
        from gen_ai_hub.orchestration_v2.service import OrchestrationService
        from tests.mock import orchestration_embeddings_v2_batch_mocker

        batch_input = EmbeddingsInput(text=["Text 1", "Text 2", "Text 3"])

        with self.ai_core_mocker(auth_url=self.proxy_client.auth_url, base_url=self.proxy_client.base_url):
            service = OrchestrationService(api_url=self.api_url, proxy_client=self.proxy_client)
            with orchestration_embeddings_v2_batch_mocker(service.api_url + '/v2/embeddings'):
                response = await service.aembed(config=self.embeddings_config, input=batch_input)

                self.assertEqual(len(response.final_result.data), 3)

    async def test_aembed_with_masking(self):
        from gen_ai_hub.orchestration_v2.service import OrchestrationService
        from tests.mock import orchestration_embeddings_v2_with_masking_mocker

        config_with_masking = EmbeddingsOrchestrationConfig(
            modules=EmbeddingsModuleConfigs(
                embeddings=EmbeddingsModelConfig(
                    model=EmbeddingsModelDetails(name="text-embedding-3-large")
                ),
                masking=MaskingModuleConfig(
                    masking_providers=[
                        MaskingProviderConfig(
                            method=MaskingMethod.ANONYMIZATION,
                            entities=[DPIStandardEntity(type=ProfileEntity.PERSON)]
                        )
                    ]
                )
            )
        )
        masked_input = EmbeddingsInput(text="Contact John Smith")

        with self.ai_core_mocker(auth_url=self.proxy_client.auth_url, base_url=self.proxy_client.base_url):
            service = OrchestrationService(api_url=self.api_url, proxy_client=self.proxy_client)
            with orchestration_embeddings_v2_with_masking_mocker(service.api_url + '/v2/embeddings'):
                response = await service.aembed(config=config_with_masking, input=masked_input)

                self.assertIsNotNone(response.intermediate_results)
                self.assertIn("input_masking", response.intermediate_results)

    async def test_aembed_timeout_parameter(self):
        from gen_ai_hub.orchestration_v2.service import OrchestrationService
        from tests.mock import GET_ORCHESTRATION_V2_EMBEDDINGS_RESPONSE
        from unittest.mock import AsyncMock, patch

        class FakeResponse:
            def raise_for_status(self):
                pass

            def json(self):
                return GET_ORCHESTRATION_V2_EMBEDDINGS_RESPONSE

        timeout_captured = {}

        async def capture_request(*args, **kwargs):
            nonlocal timeout_captured
            timeout_captured = kwargs
            return FakeResponse()

        with self.ai_core_mocker(auth_url=self.proxy_client.auth_url, base_url=self.proxy_client.base_url):
            service = OrchestrationService(api_url=self.api_url, proxy_client=self.proxy_client)
            with patch.object(service.async_client, "post", new=AsyncMock(side_effect=capture_request)):
                await service.aembed(config=self.embeddings_config, input=self.embeddings_input, timeout=90.0)
            self.assertEqual(timeout_captured.get("timeout"), 90.0)


class TestEmbeddingsRequestWithMasking(unittest.TestCase):
    """Tests for EmbeddingsRequest with data masking configuration."""

    def test_request_with_masking_config(self):
        config = EmbeddingsOrchestrationConfig(
            modules=EmbeddingsModuleConfigs(
                embeddings=EmbeddingsModelConfig(
                    model=EmbeddingsModelDetails(name="text-embedding-3-large")
                ),
                masking=MaskingModuleConfig(
                    masking_providers=[
                        MaskingProviderConfig(
                            method=MaskingMethod.ANONYMIZATION,
                            entities=[
                                DPIStandardEntity(type=ProfileEntity.PERSON),
                                DPIStandardEntity(type=ProfileEntity.EMAIL),
                            ]
                        )
                    ]
                )
            )
        )
        input_obj = EmbeddingsInput(text="Contact John at john@example.com")
        request = EmbeddingsRequest(config=config, input=input_obj)

        result = request.model_dump()
        self.assertIn("masking", result["config"]["modules"])
        masking = result["config"]["modules"]["masking"]
        self.assertEqual(len(masking["masking_providers"]), 1)
        self.assertEqual(masking["masking_providers"][0]["method"], "anonymization")

    def test_request_with_masking_allowlist(self):
        config = EmbeddingsOrchestrationConfig(
            modules=EmbeddingsModuleConfigs(
                embeddings=EmbeddingsModelConfig(
                    model=EmbeddingsModelDetails(name="text-embedding-3-large")
                ),
                masking=MaskingModuleConfig(
                    masking_providers=[
                        MaskingProviderConfig(
                            method=MaskingMethod.PSEUDONYMIZATION,
                            entities=[DPIStandardEntity(type=ProfileEntity.ORG)],
                            allowlist=["SAP", "Microsoft"]
                        )
                    ]
                )
            )
        )
        input_obj = EmbeddingsInput(text="SAP partners with Microsoft")
        request = EmbeddingsRequest(config=config, input=input_obj)

        result = request.model_dump()
        allowlist = result["config"]["modules"]["masking"]["masking_providers"][0]["allowlist"]
        self.assertEqual(allowlist, ["SAP", "Microsoft"])


if __name__ == "__main__":
    unittest.main()
