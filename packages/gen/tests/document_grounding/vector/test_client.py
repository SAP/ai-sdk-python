import unittest
from unittest.mock import patch

from gen_ai_hub.document_grounding.clients.vector_api_client import VectorAPIClient
from tests.mock import get_mocked_ai_core_client

from .mock import (
    PATH_VECTOR_API_,
    COLLECTION_ID,
    DOCUMENT_ID,
    COLLECTION,
    COLLECTIONS_LIST_RESPONSE,
    COLLECTION_CREATE_REQUEST,
    COLLECTION_CREATED_RESPONSE,
    COLLECTION_DELETED_RESPONSE,
    DOCUMENTS_CREATE_REQUEST,
    DOCUMENTS_UPDATE_REQUEST,
    DOCUMENTS_LIST_RESPONSE,
    DOCUMENTS_RESPONSE,
    DOCUMENT,
    VECTOR_SEARCH_REQUEST,
    VECTOR_SEARCH_RESPONSE,
    RESPONSE_202,
    RESPONSE_204,
)


class TestVectorAPIClient(unittest.TestCase):

    def setUp(self):
        proxy_client = get_mocked_ai_core_client(client_id='test')
        self.test_client = VectorAPIClient(proxy_client=proxy_client)

    # --- Collections ---

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.get')
    def test_get_collections(self, mock_get):
        mock_get.return_value = COLLECTIONS_LIST_RESPONSE.model_dump()
        response = self.test_client.get_collections()
        self.assertEqual(response, COLLECTIONS_LIST_RESPONSE)
        mock_get.assert_called_once_with(path=f"{PATH_VECTOR_API_}/collections", params={})

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.get')
    def test_get_collection_by_id(self, mock_get):
        mock_get.return_value = COLLECTION.model_dump()
        response = self.test_client.get_collection_by_id(COLLECTION_ID)
        self.assertEqual(response, COLLECTION)
        mock_get.assert_called_once_with(path=f"{PATH_VECTOR_API_}/collections/{COLLECTION_ID}")

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.post')
    def test_create_collection_returns_202(self, mock_post):
        """Create collection should return Response 202"""
        mock_post.return_value = ""
        response = self.test_client.create_collection(COLLECTION_CREATE_REQUEST)
        self.assertEqual(response.status_code, RESPONSE_202.status_code)
        mock_post.assert_called_once_with(
            path=f"{PATH_VECTOR_API_}/collections",
            body=COLLECTION_CREATE_REQUEST.model_dump(exclude_none=True)
        )

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.delete')
    def test_delete_collection_returns_204(self, mock_delete):
        """Delete collection should return Response 204"""
        mock_delete.return_value = ""
        response = self.test_client.delete_collection(COLLECTION_ID)
        self.assertEqual(response.status_code, RESPONSE_204.status_code)
        mock_delete.assert_called_once_with(path=f"{PATH_VECTOR_API_}/collections/{COLLECTION_ID}")

    # --- Documents ---

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.get')
    def test_get_documents(self, mock_get):
        mock_get.return_value = DOCUMENTS_RESPONSE.model_dump()
        response = self.test_client.get_documents(COLLECTION_ID)
        self.assertEqual(response, DOCUMENTS_RESPONSE)
        mock_get.assert_called_once_with(
            path=f"{PATH_VECTOR_API_}/collections/{COLLECTION_ID}/documents",
            params={}
        )

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.get')
    def test_get_document_by_id(self, mock_get):
        mock_get.return_value = DOCUMENT.model_dump()
        response = self.test_client.get_document_by_id(COLLECTION_ID, DOCUMENT_ID)
        self.assertEqual(response, DOCUMENT)
        mock_get.assert_called_once_with(
            path=f"{PATH_VECTOR_API_}/collections/{COLLECTION_ID}/documents/{DOCUMENT_ID}"
        )

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.post')
    def test_create_documents(self, mock_post):
        mock_post.return_value = DOCUMENTS_LIST_RESPONSE.model_dump()
        response = self.test_client.create_documents(COLLECTION_ID, DOCUMENTS_CREATE_REQUEST)
        self.assertEqual(response, DOCUMENTS_LIST_RESPONSE)
        mock_post.assert_called_once_with(
            path=f"{PATH_VECTOR_API_}/collections/{COLLECTION_ID}/documents",
            body=DOCUMENTS_CREATE_REQUEST.model_dump(exclude_none=True)
        )

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.patch')
    def test_update_documents(self, mock_patch):
        mock_patch.return_value = DOCUMENTS_LIST_RESPONSE.model_dump()
        response = self.test_client.update_documents(COLLECTION_ID, DOCUMENTS_UPDATE_REQUEST)
        self.assertEqual(response, DOCUMENTS_LIST_RESPONSE)
        mock_patch.assert_called_once_with(
            path=f"{PATH_VECTOR_API_}/collections/{COLLECTION_ID}/documents",
            body=DOCUMENTS_UPDATE_REQUEST.model_dump(exclude_none=True)
        )

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.delete')
    def test_delete_document_returns_204(self, mock_delete):
        mock_delete.return_value = ""
        response = self.test_client.delete_document(COLLECTION_ID, DOCUMENT_ID)
        self.assertEqual(response.status_code, RESPONSE_204.status_code)
        mock_delete.assert_called_once_with(
            path=f"{PATH_VECTOR_API_}/collections/{COLLECTION_ID}/documents/{DOCUMENT_ID}"
        )

    # --- Collection statuses ---

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.get')
    def test_get_collection_creation_status(self, mock_get):
        mock_get.return_value = COLLECTION_CREATED_RESPONSE.model_dump(by_alias=True)
        response = self.test_client.get_collection_creation_status(COLLECTION_ID)
        self.assertEqual(response.status, "CREATED")
        mock_get.assert_called_once_with(path=f"{PATH_VECTOR_API_}/collections/{COLLECTION_ID}/creationStatus")

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.get')
    def test_get_collection_deletion_status(self, mock_get):
        mock_get.return_value = COLLECTION_DELETED_RESPONSE.model_dump(by_alias=True)
        response = self.test_client.get_collection_deletion_status(COLLECTION_ID)
        self.assertEqual(response.status, "DELETED")
        mock_get.assert_called_once_with(path=f"{PATH_VECTOR_API_}/collections/{COLLECTION_ID}/deletionStatus")

    # --- Search ---

    @patch('ai_api_client_sdk.helpers.rest_client.RestClient.post')
    def test_search(self, mock_post):
        """Semantic search with filters should return structured VectorSearchResults"""
        mock_post.return_value = VECTOR_SEARCH_RESPONSE.model_dump()
        response = self.test_client.search(request=VECTOR_SEARCH_REQUEST)
        self.assertEqual(response, VECTOR_SEARCH_RESPONSE)
        mock_post.assert_called_once_with(
            path=f"{PATH_VECTOR_API_}/search",
            body=VECTOR_SEARCH_REQUEST.model_dump(exclude_none=True)
        )
