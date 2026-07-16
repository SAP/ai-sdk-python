import unittest
import time
from typing import cast

import requests.status_codes
from ai_api_client_sdk.exception import AIAPIServerException
from gen_ai_hub import GenAIHubProxyClient
from gen_ai_hub.document_grounding.client import PipelineAPIClient
from gen_ai_hub.document_grounding.models.pipeline import (
    PipelineIdResponse,
    CommonConfiguration,
    S3PipelineCreateRequest,
    GetPipelinesResponse,
    BasePipelineResponse,
    GetPipelineStatusResponse,
    SearchPipelineRequest,
    SearchPipelinesResponse,
    ManualPipelineTrigger,
    GetPipelineExecutionsResponse,
)
from gen_ai_hub.proxy import get_proxy_client
from integration_tests.test_helpers import retry_on_429_or_503_class


@retry_on_429_or_503_class()
class TestPipelinesAPIIntegration(unittest.TestCase):
    """
    Test the document-grounding API: pipelines section

    Prerequisites:
    see https://help.sap.com/docs/sap-ai-core/sap-ai-core-service-guide/create-resource-group-for-ai-data-management?q=document%20grounding&locale=en-US
    - Create or patch a resource group with the label for activating the document-grounding API.
    - Generic secrets for S3 storage should be created for the resource group.
    """

    @classmethod
    def _create_pipeline(cls):
        s3_config = S3PipelineCreateRequest(configuration=CommonConfiguration(destination="s3-secret-test-grounding"))
        return cls.client.create_pipeline(s3_config)

    @classmethod
    def setUpClass(cls):
        cls.proxy_client = cast(GenAIHubProxyClient, get_proxy_client())
        cls.client = PipelineAPIClient(proxy_client=cls.proxy_client)
        pipeline_id = cls._create_pipeline().pipelineId
        cls.pipeline_ids = [pipeline_id]

    @classmethod
    def tearDownClass(cls):
        for pipeline_id in cls.pipeline_ids:
            try:
                cls.client.delete_pipeline_by_id(pipeline_id)
            except AIAPIServerException as e:
                if e.status_code != 404:
                    raise e

    def test_create_pipeline_s3(self):
        """Test creating a pipeline for documents in S3 storage."""

        response = self._create_pipeline()
        self.pipeline_ids.append(response.pipelineId)
        self.assertIsInstance(response, PipelineIdResponse)
        self.assertIsNotNone(response.pipelineId)

    def test_get_pipelines(self):
        """Test retrieving pipelines."""
        response = self.client.get_pipelines()
        self.assertIsInstance(response, GetPipelinesResponse)
        self.assertGreaterEqual(response.count, 1)

    def test_get_pipeline_by_id(self):
        """Test retrieving a pipeline by ID."""
        pipeline_id = self.pipeline_ids[0]
        response = self.client.get_pipeline_by_id(pipeline_id)
        self.assertEqual(response.id, pipeline_id)

    def test_get_pipeline_status(self):
        """Test retrieving the status of a pipeline."""
        pipeline_id = self.pipeline_ids[0]
        response = self.client.get_pipeline_status(pipeline_id)
        self.assertIsInstance(response, GetPipelineStatusResponse)

    def test_delete_pipeline_by_id(self):
        """Test deleting a pipeline by ID."""
        new_pipeline_id = self._create_pipeline().pipelineId
        self.pipeline_ids.append(new_pipeline_id)
        # wait for the pipeline to be created
        time.sleep(3)
        response = self.client.delete_pipeline_by_id(new_pipeline_id)
        self.assertEqual(response.status_code, requests.status_codes.codes.NO_CONTENT, msg=response.text)
        self.pipeline_ids.pop(-1)

    def test_search_pipelines(self):
        """Test searching pipelines."""
        request = SearchPipelineRequest(
            dataRepositoryMetadata=[
                {"key": "description", "value": ["details"]}
         ]
        )
        response = self.client.search_pipelines(request)
        self.assertIsInstance(response, SearchPipelinesResponse)
        self.assertGreaterEqual(response.count, 0)