import json
import unittest

from gen_ai_hub.orchestration.models.config import OrchestrationConfig
from gen_ai_hub.orchestration.models.data_masking import DataMasking
from gen_ai_hub.orchestration.models.document_grounding import GroundingModule, GroundingType, DocumentGrounding, \
    DocumentGroundingFilter, GroundingFilterSearch, DataRepositoryType
from gen_ai_hub.orchestration.models.llm import LLM
from gen_ai_hub.orchestration.models.message import SystemMessage, UserMessage
from gen_ai_hub.orchestration.models.sap_data_privacy_integration import SAPDataPrivacyIntegration, MaskingMethod, \
    ProfileEntity
from gen_ai_hub.orchestration.models.template import Template, TemplateValue
from gen_ai_hub.orchestration.service import OrchestrationService
from integration_tests.orchestration.test_base import OrchestrationServiceTestBase
from integration_tests.test_helpers import retry_on_429_or_503_class, retry_on_429_or_503


@retry_on_429_or_503_class()
class TestGrounding(OrchestrationServiceTestBase):

    def setUp(self):
        super().setUp()
        self.service = OrchestrationService(api_url=self.api_url)
        self.llm = LLM(
            name="gpt-4o",
            parameters={
                'temperature': 0.0,
            }
        )
        self.template = Template(
            messages=[
                SystemMessage("You are a friendly assistant."),
                UserMessage("Question: {{?user_query}}\n Context: {{?grounding_response}}"),
            ]
        )

    def test_no_filter(self):
        """
        Run orchestration service with default / empty grounding configuration.
        """
        grounding_config = GroundingModule(
            type=GroundingType.DOCUMENT_GROUNDING_SERVICE.value,
            config=DocumentGrounding(input_params=["user_query"], output_param="grounding_response")
        )

        config = OrchestrationConfig(
            template=self.template,
            llm=self.llm,
            grounding=grounding_config
        )

        response = self.service.run(config=config,
                                    template_values=[
                                        TemplateValue("user_query", "What is the orchestration service?"),
                                    ])

        self.assertIn("orchestration service", response.orchestration_result.choices[0].message.content)

    def test_grounding_SAPHelp(self):
        """
        This tests the grounding option "elastic search" which is enabled for SAP Help website.
        The indexed search is used instead of embedding vectors.
        This is the minimal setup required for a grounding use case.
        """

        filters = [
            DocumentGroundingFilter(id="SAPHelp", data_repository_type="help.sap.com")
        ]

        grounding_config = GroundingModule(
            type=GroundingType.DOCUMENT_GROUNDING_SERVICE.value,
            config=DocumentGrounding(input_params=["user_query"], output_param="grounding_response", filters=filters)
        )

        config = OrchestrationConfig(
            template=self.template,
            llm=self.llm,
            grounding=grounding_config
        )

        response = self.service.run(config=config,
                                    template_values=[
                                        TemplateValue("user_query", "What is SAP AI Core?"),
                                    ])

        print(response.orchestration_result.choices[0].message.content)
        self.assertIn("SAP AI Core", response.orchestration_result.choices[0].message.content)

    def test_grounding_vector(self):
        """
        Test grounding based on vector store created with Data API.
        Metadata keys point to sources of the documents.
        """
        metadata_keys = ['source', 'webUrl', 'title', 'mimeType', 'fileSuffix']
        filters = [DocumentGroundingFilter(id="s3-docs",
                                           data_repositories=["46b508c9-e490-4808-893b-b8e3361c4213"],
                                           search_config=GroundingFilterSearch(max_chunk_count=2),
                                           data_repository_type=DataRepositoryType.VECTOR.value
                                          )
                   ]

        grounding_config = GroundingModule(
            type=GroundingType.DOCUMENT_GROUNDING_SERVICE.value,
            config=DocumentGrounding(input_params=["user_query"], output_param="grounding_response", filters=filters,
                                     metadata_params= metadata_keys)
        )

        orchestration_template = Template(
            messages=[
                SystemMessage("""Facility Solutions Company provides services to luxury residential complexes, apartments, 
                individual homes, and commercial properties such as office buildings, retail spaces, industrial facilities, and educational institutions. 
                Customers are encouraged to reach out with maintenance requests, service deficiencies, follow-ups, or any issues they need by email.
                """),
                UserMessage("""You are a helpful assistant for any queries for answering questions.
                Answer the request by providing relevant answers that fit to the request.
                Request: {{ ?user_query }}
                Context:{{ ?grounding_response }}
                """),
            ]
        )

        config = OrchestrationConfig(
            template=orchestration_template,
            llm=self.llm,
            grounding=grounding_config
        )

        response = self.service.run(config=config,
                                    template_values=[
                                        TemplateValue("user_query", "Is there a complaint?"),
                                    ])
        self.assertIsNotNone(response.module_results.grounding)
        metadata = json.loads(response.module_results.grounding.data['grounding_result'])[0]['metadata']
        for key in metadata_keys:
            self.assertIn(key, metadata.keys())
        self.assertIn("complaint", response.orchestration_result.choices[0].message.content)

    @unittest.skip("Required setting up sharepoint.")
    def test_grounding_sharepoint(self):  # technical user for sharepoint not available
        pass

    def test_grounding_with_data_masking_enabled(self):
        filters = [
            DocumentGroundingFilter(id="SAPHelp", data_repository_type="help.sap.com")
        ]

        grounding_config = GroundingModule(
            type=GroundingType.DOCUMENT_GROUNDING_SERVICE.value,
            config=DocumentGrounding(input_params=["user_query"], output_param="grounding_response", filters=filters)
        )

        data_masking = DataMasking(
            providers=[
                SAPDataPrivacyIntegration(
                    method=MaskingMethod.ANONYMIZATION,
                    entities=[
                        ProfileEntity.ORG
                    ],
                    mask_grounding_input=True
                )
            ])

        config = OrchestrationConfig(
            template=self.template,
            llm=self.llm,
            grounding=grounding_config,
            data_masking=data_masking
        )

        response = self.service.run(config=config,
                                    template_values=[
                                        TemplateValue("user_query", "What is SAP AI Core?"),
                                    ])

        self.assertIsNotNone(response.module_results.input_masking.data.get('masked_grounding_input'))

    def test_grounding_with_data_masking_disabled(self):
        filters = [
            DocumentGroundingFilter(id="SAPHelp", data_repository_type="help.sap.com")
        ]

        grounding_config = GroundingModule(
            type=GroundingType.DOCUMENT_GROUNDING_SERVICE.value,
            config=DocumentGrounding(input_params=["user_query"], output_param="grounding_response", filters=filters)
        )

        data_masking = DataMasking(
            providers=[
                SAPDataPrivacyIntegration(
                    method=MaskingMethod.ANONYMIZATION,
                    entities=[
                        ProfileEntity.ORG
                    ],
                    mask_grounding_input=False
                )
            ])

        config = OrchestrationConfig(
            template=self.template,
            llm=self.llm,
            grounding=grounding_config,
            data_masking=data_masking
        )

        response = self.service.run(config=config,
                                    template_values=[
                                        TemplateValue("user_query", "What is SAP AI Core?"),
                                    ])

        self.assertIsNone(response.module_results.input_masking.data.get('masked_grounding_input'))
