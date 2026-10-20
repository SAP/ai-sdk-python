import unittest
from unittest.mock import patch

from gen_ai_hub.document_grounding.clients.retrieval_api_client import RetrievalAPIClient
from tests.mock import get_mocked_ai_core_client

from .mock import (
    PATH_RETRIEVAL_API_,
    DATA_REPOSITORIES_RESPONSE,
    DATA_REPOSITORY_RESPONSE,
    RETRIEVAL_SEARCH_INPUT,
    RETRIEVAL_SEARCH_RESULT,
)


class TestRetrievalAPIClient(unittest.TestCase):

    def setUp(self):
        proxy_client = get_mocked_ai_core_client(client_id='test')
        self.test_client = RetrievalAPIClient(proxy_client=proxy_client)

    # --- Data Repositories ---

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.get')
    def test_get_data_repositories(self, mock_get):
        """List all data repositories should return structured DataRepositoriesResponse"""
        mock_get.return_value = DATA_REPOSITORIES_RESPONSE.model_dump()
        response = self.test_client.get_data_repositories()
        self.assertEqual(response, DATA_REPOSITORIES_RESPONSE)
        mock_get.assert_called_once_with(path=f"{PATH_RETRIEVAL_API_}/dataRepositories", params={})

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.get')
    def test_get_data_repository_by_id(self, mock_get):
        """Get single data repository by ID should return DataRepository"""
        repository_id = DATA_REPOSITORY_RESPONSE.id
        mock_get.return_value = DATA_REPOSITORY_RESPONSE.model_dump()
        response = self.test_client.get_data_repository_by_id(repository_id)
        self.assertEqual(response, DATA_REPOSITORY_RESPONSE)
        mock_get.assert_called_once_with(path=f"{PATH_RETRIEVAL_API_}/dataRepositories/{repository_id}")

    # --- Search ---

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.post')
    def test_search(self, mock_post):
        """Retrieval search should return structured RetrievalSearchResults"""
        mock_post.return_value = RETRIEVAL_SEARCH_RESULT.model_dump()
        response = self.test_client.search(RETRIEVAL_SEARCH_INPUT)
        self.assertEqual(response, RETRIEVAL_SEARCH_RESULT)
        mock_post.assert_called_once_with(
            path=f"{PATH_RETRIEVAL_API_}/search",
            body=RETRIEVAL_SEARCH_INPUT.model_dump(exclude_none=True)
        )
