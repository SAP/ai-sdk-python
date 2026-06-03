import json
import unittest

from gen_ai_hub.orchestration_v2.models.config import OrchestrationConfig, ModuleConfig
from gen_ai_hub.orchestration_v2.models.data_masking import MaskingModuleConfig, DPIStandardEntity, ProfileEntity, \
    MaskingProviderConfig, MaskingMethod, MaskGroundingInput
from gen_ai_hub.orchestration_v2.models.document_grounding import (GroundingModuleConfig, GroundingType, DataRepositoryType,
                                                                   DocumentGroundingConfig, DocumentGroundingFilter,
                                                                   DocumentGroundingPlaceholders, GroundingSearchConfig)
from gen_ai_hub.orchestration_v2.models.llm_model_details import LLMModelDetails
from gen_ai_hub.orchestration_v2.models.message import SystemMessage, UserMessage
from gen_ai_hub.orchestration_v2.models.template import Template, PromptTemplatingModuleConfig
from gen_ai_hub.orchestration_v2.service import OrchestrationService
from integration_tests.orchestration_v2.test_base import OrchestrationServiceTestBase
from integration_tests.test_helpers import with_retry_on_missing_resource, retry_on_429_or_503


class TestGrounding(OrchestrationServiceTestBase):

    def setUp(self):
        super().setUp()
        self.service = OrchestrationService(api_url=self.api_url)
        self.llm = LLMModelDetails(
            name="gpt-4o",
            params={
                'temperature': 0.0,
            }
        )
        self.template = Template(template=[
            SystemMessage(content="You are a friendly assistant."),
            UserMessage(content="Question: {{?user_query}}\n Context: {{?grounding_response}}")
        ]
        )

    @retry_on_429_or_503(max_retries=3, initial_delay=2.0, backoff_factor=2.0)
    def test_no_filter(self):
        """
        Run orchestration service with default / empty grounding configuration.
        """
        grounding_config = GroundingModuleConfig(
            type=GroundingType.DOCUMENT_GROUNDING_SERVICE.value,
            config=DocumentGroundingConfig(
                placeholders=DocumentGroundingPlaceholders(input=["user_query"], output="grounding_response")
            )
        )

        config = OrchestrationConfig(
            modules=ModuleConfig(prompt_templating=PromptTemplatingModuleConfig(prompt=self.template, model=self.llm),
                                 grounding=grounding_config)
        )

        response = self.service.run(config=config,
                                    placeholder_values=({"user_query": "What is the orchestration service?"}),
                                    )

        self.assertIn("orchestration service", response.final_result.choices[0].message.content.lower())

    @retry_on_429_or_503(max_retries=3, initial_delay=2.0, backoff_factor=2.0)
    def test_grounding_SAPHelp(self):
        """
        This tests the grounding option "elastic search" which is enabled for SAP Help website.
        The indexed search is used instead of embedding vectors.
        This is the minimal setup required for a grounding use case.
        """

        filters = [
            DocumentGroundingFilter(id="SAPHelp", data_repository_type="help.sap.com")
        ]

        grounding_config = GroundingModuleConfig(
            type=GroundingType.DOCUMENT_GROUNDING_SERVICE.value,
            config=DocumentGroundingConfig(
                placeholders=DocumentGroundingPlaceholders(input=["user_query"], output="grounding_response"),
                filters=filters
            )
        )

        config = OrchestrationConfig(
            modules=ModuleConfig(prompt_templating=PromptTemplatingModuleConfig(prompt=self.template, model=self.llm),
                                 grounding=grounding_config)
        )

        response = self.service.run(config=config,
                                    placeholder_values=(
                                        {"user_query": "What is the SAP AI Core orchestration service?"}),
                                    )

        self.assertIn("SAP AI Core", response.final_result.choices[0].message.content)

    @with_retry_on_missing_resource(max_retries=3, delay=2.0)
    def test_grounding_vector(self):
        """
        Test grounding based on vector store created with Data API.
        Metadata keys point to sources of the documents.
        """
        metadata_keys = ['source', 'webUrl', 'title', 'mimeType', 'fileSuffix']
        filters = [DocumentGroundingFilter(id="s3-docs",
                                           data_repositories=["46b508c9-e490-4808-893b-b8e3361c4213"],
                                           search_config=GroundingSearchConfig(max_chunk_count=2),
                                           data_repository_type=DataRepositoryType.VECTOR.value
                                           )
                   ]

        grounding = GroundingModuleConfig(
            type=GroundingType.DOCUMENT_GROUNDING_SERVICE.value,
            config=DocumentGroundingConfig(filters=filters,
                                           placeholders={'input': ["user_query"], 'output': "grounding_response"},
                                           metadata_params=metadata_keys
                                           )
        )

        orchestration_template = Template(template=[
            SystemMessage(content="""Facility Solutions Company provides services to luxury residential complexes, apartments,
                individual homes, and commercial properties such as office buildings, retail spaces, industrial facilities, and educational institutions.
                Customers are encouraged to reach out with maintenance requests, service deficiencies, follow-ups, or any issues they need by email.
                """),
            UserMessage(content="""You are a helpful assistant for any queries for answering questions.
                Answer the request by providing relevant answers that fit to the request.
                Request: {{ ?user_query }}
                Context:{{ ?grounding_response }}
                """),
        ]
        )

        config = OrchestrationConfig(
            modules=ModuleConfig(
                prompt_templating=PromptTemplatingModuleConfig(prompt=orchestration_template, model=self.llm),
                grounding=grounding
            )
        )

        response = self.service.run(config=config,
                                    placeholder_values=({"user_query": "Is there a complaint?"})
                                    )
        self.assertIsNotNone(response.intermediate_results.grounding)
        metadata = json.loads(response.intermediate_results.grounding.data['grounding_result'])[0]['metadata']
        for key in metadata_keys:
            self.assertIn(key, metadata.keys())
        self.assertIn("complaint", response.final_result.choices[0].message.content)

    @unittest.skip("Required setting up sharepoint.")
    def test_grounding_sharepoint(self):  # technical user for sharepoint not available
        pass

    @retry_on_429_or_503(max_retries=3, initial_delay=2.0, backoff_factor=2.0)
    def test_grounding_with_data_masking_enabled(self):
        filters = [
            DocumentGroundingFilter(id="SAPHelp", data_repository_type="help.sap.com")
        ]

        grounding_config = GroundingModuleConfig(
            type=GroundingType.DOCUMENT_GROUNDING_SERVICE.value,
            config=DocumentGroundingConfig(
                placeholders=DocumentGroundingPlaceholders(input=["user_query"], output="grounding_response"),
                filters=filters
            )
        )

        data_masking = MaskingModuleConfig(providers=[
            MaskingProviderConfig(
                    method=MaskingMethod.ANONYMIZATION,
                    entities=[DPIStandardEntity(type=ProfileEntity.ORG)],
                    mask_grounding_input=MaskGroundingInput(enabled=True)
                )
            ])

        config = OrchestrationConfig(
            modules=ModuleConfig(prompt_templating=PromptTemplatingModuleConfig(prompt=self.template, model=self.llm),
                                 grounding=grounding_config,
                                 masking=data_masking
                                )
        )

        response = self.service.run(config=config,
                                    placeholder_values=({"user_query": "What is SAP AI Core?"})
                                   )

        self.assertIsNotNone(response.intermediate_results.input_masking.data.get('masked_template'))
        self.assertIn("MASKED_ORG", response.final_result.choices[0].message.content)
