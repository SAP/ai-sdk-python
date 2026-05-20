import unittest
from unittest.mock import patch

import requests
from gen_ai_hub.document_grounding.client import PipelineAPIClient
from gen_ai_hub.document_grounding.models.pipeline import S3PipelineCreateRequest, CommonConfiguration
from tests.mock import get_mocked_ai_core_client

from .mock import (
    GET_PIPELINE_STATUS_RESPONSE,
    PIPELINE_ID_RESPONSE,
    GET_PIPELINES_RESPONSE,
    PATH_PIPELINES_API_,
    BASE_PIPELINE_RESPONSE,
    PIPELINE_ID,
    SEARCH_PIPELINES_REQUEST,
    SEARCH_PIPELINES_RESPONSE,
    GET_EXECUTIONS_RESPONSE,
    GET_EXECUTION_BY_ID_RESPONSE,
    EXECUTION_ID_1,
    GET_EXECUTION_DOCUMENTS_RESPONSE,
    GET_EXECUTION_DOCUMENT_BY_ID_RESPONSE,
    DOCUMENT_ID_1,
    GET_PIPELINE_DOCUMENTS_RESPONSE,
    GET_PIPELINE_DOCUMENT_BY_ID_RESPONSE,
    DOCUMENT_ID_4,
    MANUAL_TRIGGER_REQUEST,
)


class TestPipelineAPIClient(unittest.TestCase):

    def setUp(self):
        proxy_client = get_mocked_ai_core_client(client_id='test')
        self.test_client = PipelineAPIClient(proxy_client=proxy_client)

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.get')
    def test_get_pipelines(self, mock_get):
        mock_get.return_value = GET_PIPELINES_RESPONSE.model_dump()
        response = self.test_client.get_pipelines(
            top=10,
            skip=5,
            count=True,
        )
        self.assertEqual(response, GET_PIPELINES_RESPONSE)
        self.assertEqual(response.count, 2)
        mock_get.assert_called_once_with(
            path=PATH_PIPELINES_API_,
            params={"$top": 10, "$skip": 5, "$count": True}
        )

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.get')
    def test_get_pipeline_by_id(self, mock_get):
        mock_get.return_value = BASE_PIPELINE_RESPONSE.model_dump()
        response = self.test_client.get_pipeline_by_id(PIPELINE_ID)
        self.assertEqual(response, BASE_PIPELINE_RESPONSE)
        self.assertEqual(response.id, BASE_PIPELINE_RESPONSE.id)
        mock_get.assert_called_once_with(path=PATH_PIPELINES_API_ + f'/{PIPELINE_ID}')

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.get')
    def test_get_pipeline_status(self, mock_get):
        mock_get.return_value = GET_PIPELINE_STATUS_RESPONSE.model_dump()
        response = self.test_client.get_pipeline_status(PIPELINE_ID)
        self.assertEqual(response, GET_PIPELINE_STATUS_RESPONSE)
        self.assertEqual(response.status, 'FINISHED')
        mock_get.assert_called_once_with(path=PATH_PIPELINES_API_ + f'/{PIPELINE_ID}/status')

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.post')
    def test_create_pipeline(self, mock_post):
        ppl_req = S3PipelineCreateRequest(configuration=CommonConfiguration(destination="s3-secret"))
        mock_post.return_value = PIPELINE_ID_RESPONSE.model_dump()
        response = self.test_client.create_pipeline(pipeline_request=ppl_req)
        self.assertEqual(response, PIPELINE_ID_RESPONSE)
        mock_post.assert_called_once_with(path=PATH_PIPELINES_API_, body=ppl_req.model_dump(exclude_none=True))

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.delete')
    def test_delete_pipeline_by_id(self, mock_delete=None):
        mock_delete.return_value = ""
        response = self.test_client.delete_pipeline_by_id(PIPELINE_ID)
        self.assertEqual(response.status_code, 204)
        mock_delete.assert_called_once_with(path=PATH_PIPELINES_API_ + f'/{PIPELINE_ID}')

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.post')
    def test_search_pipelines(self, mock_post):
        mock_post.return_value = SEARCH_PIPELINES_RESPONSE.model_dump()
        resp = self.test_client.search_pipelines(SEARCH_PIPELINES_REQUEST)

        self.assertEqual(resp, SEARCH_PIPELINES_RESPONSE)
        self.assertEqual(resp.count, 1)
        self.assertEqual(resp.resources[0].pipelineId, PIPELINE_ID)

        mock_post.assert_called_once_with(
            path=f"{PATH_PIPELINES_API_}/search",
            body=SEARCH_PIPELINES_REQUEST.model_dump(exclude_none=True),
            )

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.get')
    def test_get_pipeline_executions_no_params(self, mock_get):
        mock_get.return_value = GET_EXECUTIONS_RESPONSE.model_dump()
        resp = self.test_client.get_pipeline_executions(pipeline_id=PIPELINE_ID)

        self.assertEqual(resp, GET_EXECUTIONS_RESPONSE)
        self.assertEqual(resp.count, 2)
        self.assertEqual(len(resp.resources), 2)

        mock_get.assert_called_once_with(
            path=f"{PATH_PIPELINES_API_}/{PIPELINE_ID}/executions",
            params={},
        )

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.get')
    def test_get_pipeline_executions_with_params(self, mock_get):
        mock_get.return_value = GET_EXECUTIONS_RESPONSE.model_dump()
        resp = self.test_client.get_pipeline_executions(
            pipeline_id=PIPELINE_ID,
            last_execution=True,
            top=10,
            skip=5,
            count=True,
        )

        self.assertEqual(resp.count, 2)

        mock_get.assert_called_once_with(
            path=f"{PATH_PIPELINES_API_}/{PIPELINE_ID}/executions",
            params={"lastExecution": True, "$top": 10, "$skip": 5, "$count": True},
        )

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.get')
    def test_get_pipeline_execution_by_id(self, mock_get):
        mock_get.return_value = GET_EXECUTION_BY_ID_RESPONSE.model_dump()
        resp = self.test_client.get_pipeline_execution_by_id(
            pipeline_id=PIPELINE_ID,
            execution_id=EXECUTION_ID_1,
        )

        self.assertEqual(resp, GET_EXECUTION_BY_ID_RESPONSE)
        self.assertEqual(resp.id, EXECUTION_ID_1)

        mock_get.assert_called_once_with(
            path=f"{PATH_PIPELINES_API_}/{PIPELINE_ID}/executions/{EXECUTION_ID_1}"
        )

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.get')
    def test_get_execution_documents(self, mock_get):
        mock_get.return_value = GET_EXECUTION_DOCUMENTS_RESPONSE.model_dump()
        resp = self.test_client.get_execution_documents(
            pipeline_id=PIPELINE_ID,
            execution_id=EXECUTION_ID_1,
            top=50,
            skip=0,
            count=True,
        )

        self.assertEqual(resp.count, 2)
        self.assertEqual(len(resp.resources), 2)

        mock_get.assert_called_once_with(
            path=f"{PATH_PIPELINES_API_}/{PIPELINE_ID}/executions/{EXECUTION_ID_1}/documents",
            params={"$top": 50, "$skip": 0, "$count": True},
        )

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.get')
    def test_get_execution_document_by_id(self, mock_get):
        mock_get.return_value = GET_EXECUTION_DOCUMENT_BY_ID_RESPONSE.model_dump()
        resp = self.test_client.get_execution_document_by_id(
            pipeline_id=PIPELINE_ID,
            execution_id=EXECUTION_ID_1,
            document_id=DOCUMENT_ID_1,
        )

        self.assertEqual(resp, GET_EXECUTION_DOCUMENT_BY_ID_RESPONSE)
        self.assertEqual(resp.id, DOCUMENT_ID_1)

        mock_get.assert_called_once_with(
            path=f"{PATH_PIPELINES_API_}/{PIPELINE_ID}/executions/{EXECUTION_ID_1}/documents/{DOCUMENT_ID_1}"
        )

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.get')
    def test_get_pipeline_documents(self, mock_get):
        mock_get.return_value = GET_PIPELINE_DOCUMENTS_RESPONSE.model_dump()
        resp = self.test_client.get_pipeline_documents(
            pipeline_id=PIPELINE_ID,
            top=25,
            skip=5,
            count=False,
        )

        self.assertEqual(resp.count, 2)
        self.assertEqual(len(resp.resources), 2)

        mock_get.assert_called_once_with(
            path=f"{PATH_PIPELINES_API_}/{PIPELINE_ID}/documents",
            params={"$top": 25, "$skip": 5, "$count": False},
        )

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.get')
    def test_get_pipeline_document_by_id(self, mock_get):
        mock_get.return_value = GET_PIPELINE_DOCUMENT_BY_ID_RESPONSE.model_dump()
        resp = self.test_client.get_pipeline_document_by_id(
            pipeline_id=PIPELINE_ID,
            document_id=DOCUMENT_ID_4,
        )

        self.assertEqual(resp, GET_PIPELINE_DOCUMENT_BY_ID_RESPONSE)
        self.assertEqual(resp.id, DOCUMENT_ID_4)

        mock_get.assert_called_once_with(
            path=f"{PATH_PIPELINES_API_}/{PIPELINE_ID}/documents/{DOCUMENT_ID_4}"
        )

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.post')
    def test_trigger_pipeline_empty_string_returns_202(self, mock_post):
        mock_post.return_value = ""
        resp = self.test_client.trigger_pipeline(MANUAL_TRIGGER_REQUEST)

        self.assertIsInstance(resp, requests.Response)
        self.assertEqual(resp.status_code, 202)

        mock_post.assert_called_once_with(
            path=f"{PATH_PIPELINES_API_}/trigger",
            body=MANUAL_TRIGGER_REQUEST.model_dump(exclude_none=True),
        )
