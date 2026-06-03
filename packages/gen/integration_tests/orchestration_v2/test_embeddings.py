import unittest

from gen_ai_hub.orchestration_v2.models.embeddings import (
    EmbeddingsOrchestrationConfig,
    EmbeddingsModuleConfigs,
    EmbeddingsModelConfig,
    EmbeddingsModelDetails,
    EmbeddingsModelParams,
    EmbeddingsInput,
    EmbeddingsInputType,
    EmbeddingsPostResponse,
)
from gen_ai_hub.orchestration_v2.models.data_masking import (
    MaskingModuleConfig,
    MaskingProviderConfig,
    MaskingMethod,
    DPIStandardEntity,
    ProfileEntity,
)
from gen_ai_hub.orchestration_v2.service import OrchestrationService
from integration_tests.orchestration_v2.test_base import OrchestrationServiceTestBase
from integration_tests.test_helpers import retry_on_429_or_503_class


@retry_on_429_or_503_class()
class TestEmbeddings(OrchestrationServiceTestBase):
    """Integration tests for embeddings endpoint."""

    def setUp(self):
        super().setUp()
        self.service = OrchestrationService(api_url=self.api_url)
        self.base_config = EmbeddingsOrchestrationConfig(
            modules=EmbeddingsModuleConfigs(
                embeddings=EmbeddingsModelConfig(
                    model=EmbeddingsModelDetails(name="text-embedding-3-small")
                )
            )
        )

    def test_embed_single_text(self):
        """Test generating embedding for a single text."""
        response = self.service.embed(
            config=self.base_config,
            input=EmbeddingsInput(text="Hello World!")
        )

        self.assertIsInstance(response, EmbeddingsPostResponse)
        self.assertIsNotNone(response.request_id)
        self.assertEqual(len(response.final_result.data), 1)
        self.assertEqual(response.final_result.data[0].index, 0)
        self.assertIsInstance(response.final_result.data[0].embedding, list)
        self.assertGreater(len(response.final_result.data[0].embedding), 0)
        # Verify usage info is returned
        self.assertGreater(response.final_result.usage.prompt_tokens, 0)
        self.assertGreater(response.final_result.usage.total_tokens, 0)

    def test_embed_batch_texts(self):
        """Test generating embeddings for multiple texts in a single request."""
        documents = [
            "First document.",
            "Second document.",
            "Third document."
        ]
        response = self.service.embed(
            config=self.base_config,
            input=EmbeddingsInput(text=documents)
        )

        self.assertEqual(len(response.final_result.data), 3)
        for i, result in enumerate(response.final_result.data):
            self.assertEqual(result.index, i)

    def test_embed_with_model_params(self):
        """Test embedding with custom model parameters (dimensions, normalize, encoding_format)."""
        import math
        from gen_ai_hub.orchestration_v2.models.embeddings import EmbeddingsEncodingFormat

        # Test dimensions + normalize (with default float encoding)
        config = EmbeddingsOrchestrationConfig(
            modules=EmbeddingsModuleConfigs(
                embeddings=EmbeddingsModelConfig(
                    model=EmbeddingsModelDetails(
                        name="text-embedding-3-small",
                        params=EmbeddingsModelParams(
                            dimensions=256,
                            normalize=True
                        )
                    )
                )
            )
        )

        response = self.service.embed(
            config=config,
            input=EmbeddingsInput(text="Test model parameters")
        )

        embedding = response.final_result.data[0].embedding
        # Verify dimensions
        self.assertEqual(len(embedding), 256)
        # Verify normalize: L2 norm should be ~1
        l2_norm = math.sqrt(sum(x * x for x in embedding))
        self.assertAlmostEqual(l2_norm, 1.0, places=4)

        # Test base64 encoding format
        config_base64 = EmbeddingsOrchestrationConfig(
            modules=EmbeddingsModuleConfigs(
                embeddings=EmbeddingsModelConfig(
                    model=EmbeddingsModelDetails(
                        name="text-embedding-3-small",
                        params=EmbeddingsModelParams(
                            encoding_format=EmbeddingsEncodingFormat.BASE64
                        )
                    )
                )
            )
        )

        response = self.service.embed(
            config=config_base64,
            input=EmbeddingsInput(text="Test base64 encoding")
        )

        # Base64 returns a string
        self.assertIsInstance(response.final_result.data[0].embedding, str)

    def test_embed_with_input_types(self):
        """Test embedding with different input type hints (document, query)."""
        # Document type
        response = self.service.embed(
            config=self.base_config,
            input=EmbeddingsInput(
                text="SAP is a German multinational software company.",
                type=EmbeddingsInputType.DOCUMENT
            )
        )
        self.assertGreater(len(response.final_result.data[0].embedding), 0)

        # Query type
        response = self.service.embed(
            config=self.base_config,
            input=EmbeddingsInput(
                text="What is SAP?",
                type=EmbeddingsInputType.QUERY
            )
        )
        self.assertGreater(len(response.final_result.data[0].embedding), 0)

    def test_embed_with_data_masking(self):
        """Test embedding with PII data masking and allowlist."""
        config = EmbeddingsOrchestrationConfig(
            modules=EmbeddingsModuleConfigs(
                embeddings=EmbeddingsModelConfig(
                    model=EmbeddingsModelDetails(name="text-embedding-3-small")
                ),
                masking=MaskingModuleConfig(
                    masking_providers=[
                        MaskingProviderConfig(
                            method=MaskingMethod.ANONYMIZATION,
                            entities=[
                                DPIStandardEntity(type=ProfileEntity.PERSON),
                                DPIStandardEntity(type=ProfileEntity.EMAIL),
                            ],
                            allowlist=["SAP"]
                        )
                    ]
                )
            )
        )

        response = self.service.embed(
            config=config,
            input=EmbeddingsInput(
                text="Contact John Smith at john@example.com about SAP."
            )
        )

        self.assertIsNotNone(response.intermediate_results)
        self.assertIn("input_masking", response.intermediate_results)
        # Verify allowlisted term is preserved
        masked_input = response.intermediate_results["input_masking"]["data"]["masked_input"]
        self.assertIn("SAP", masked_input)
        self.assertGreater(len(response.final_result.data[0].embedding), 0)


    def test_embed_with_model_version(self):
        """Test embedding with specific model version."""
        config = EmbeddingsOrchestrationConfig(
            modules=EmbeddingsModuleConfigs(
                embeddings=EmbeddingsModelConfig(
                    model=EmbeddingsModelDetails(
                        name="text-embedding-3-small",
                        version="latest"
                    )
                )
            )
        )

        response = self.service.embed(
            config=config,
            input=EmbeddingsInput(text="Test model version")
        )

        self.assertIsInstance(response, EmbeddingsPostResponse)
        self.assertGreater(len(response.final_result.data[0].embedding), 0)

    def test_embed_invalid_model_name(self):
        """Test that invalid model name raises an error."""
        from gen_ai_hub.orchestration_v2.exceptions import OrchestrationError

        config = EmbeddingsOrchestrationConfig(
            modules=EmbeddingsModuleConfigs(
                embeddings=EmbeddingsModelConfig(
                    model=EmbeddingsModelDetails(name="non-existent-model-xyz")
                )
            )
        )

        with self.assertRaises(OrchestrationError):
            self.service.embed(
                config=config,
                input=EmbeddingsInput(text="This should fail")
            )


@retry_on_429_or_503_class()
class TestEmbeddingsAsync(OrchestrationServiceTestBase, unittest.IsolatedAsyncioTestCase):
    """Async integration tests for embeddings endpoint."""

    async def asyncSetUp(self):
        self.service = OrchestrationService(api_url=self.api_url)
        self.config = EmbeddingsOrchestrationConfig(
            modules=EmbeddingsModuleConfigs(
                embeddings=EmbeddingsModelConfig(
                    model=EmbeddingsModelDetails(name="text-embedding-3-small")
                )
            )
        )

    async def test_aembed_single_text(self):
        """Test async embedding for a single text."""
        response = await self.service.aembed(
            config=self.config,
            input=EmbeddingsInput(text="Hello async world!")
        )
        self.assertIsInstance(response, EmbeddingsPostResponse)
        self.assertGreater(len(response.final_result.data[0].embedding), 0)
        await self.service.aclose_http_connection()

    async def test_aembed_batch_texts(self):
        """Test async embedding for batch texts."""
        response = await self.service.aembed(
            config=self.config,
            input=EmbeddingsInput(text=["First", "Second"])
        )
        self.assertEqual(len(response.final_result.data), 2)
        await self.service.aclose_http_connection()


if __name__ == "__main__":
    unittest.main()
