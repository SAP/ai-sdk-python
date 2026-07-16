import unittest
from typing import cast
import requests

from .. import get_random_string
from gen_ai_hub import GenAIHubProxyClient
from gen_ai_hub.document_grounding.clients.retrieval_api_client import RetrievalAPIClient
from gen_ai_hub.document_grounding.clients.vector_api_client import VectorAPIClient
from gen_ai_hub.document_grounding.models.retrieval import (
    RetrievalSearchInput,
    RetrievalSearchFilter,
    RetrievalSearchConfiguration,
    RetrievalSearchDocumentKeyValueListPair,
    DataRepositories,
    DataRepository,
    RetrievalSearchResults,
    RetrievalSearchResults,
    RetrievalPerFilterSearchResult,
    RetrievalDataRepositorySearchResult,
    DataRepositoryWithDocuments,
    RetrievalDocument,
    RetrievalChunk,
)
from gen_ai_hub.document_grounding.models.vector import (
    CollectionCreateRequest,
    EmbeddingConfig,
    VectorKeyValueListPair,
    BaseDocument,
    TextOnlyBaseChunk,
    DocumentsCreateRequest,
)
from gen_ai_hub.proxy import get_proxy_client
from integration_tests.test_helpers import retry_on_429_or_503_class


@retry_on_429_or_503_class()
class TestRetrievalAPIIntegration(unittest.TestCase):
    """
    Integration test suite for the Retrieval API.

    Focuses on:
      - Data repositories listing and details
      - Retrieval search across vector repositories

    Prerequisites:
      - Valid access configuration.
    """

    @classmethod
    def setUpClass(cls):
        """Prepare test data — create a vector collection and document for retrieval testing."""
        cls.proxy_client = cast(GenAIHubProxyClient, get_proxy_client())
        cls.vector_client = VectorAPIClient(proxy_client=cls.proxy_client)
        cls.retrieval_client = RetrievalAPIClient(proxy_client=cls.proxy_client)

        # --- Create test vector collection ---
        cls.collection_title = f"retrieval-integration-test-collection-{get_random_string()}"
        create_request = CollectionCreateRequest(
            title=cls.collection_title,
            embeddingConfig=EmbeddingConfig(modelName="text-embedding-3-large"),
            metadata=[
                VectorKeyValueListPair(key="purpose", value=["retrieval-test"]),
                VectorKeyValueListPair(key="source", value=["integration"]),
            ],
        )
        create_resp = cls.vector_client.create_collection(create_request)
        assert create_resp.status_code == requests.status_codes.codes.ACCEPTED

        list_resp = cls.vector_client.get_collections()
        assert list_resp.resources
        for res in list_resp.resources:
            if res.title == cls.collection_title:
                cls.collection_id = res.id

        # --- Create test document ---
        doc = BaseDocument(
            metadata=[VectorKeyValueListPair(key="url", value=["http://retrieval-test.com"])],
            chunks=[
                TextOnlyBaseChunk(
                    content="Joule is an AI copilot that helps automate SAP workflows.",
                    metadata=[VectorKeyValueListPair(key="index", value=["1"])],
                ),
                TextOnlyBaseChunk(
                    content="It understands enterprise context and enhances productivity.",
                    metadata=[VectorKeyValueListPair(key="index", value=["2"])],
                ),
            ],
        )
        create_doc_resp = cls.vector_client.create_documents(cls.collection_id, DocumentsCreateRequest(documents=[doc]))
        cls.document_id = create_doc_resp.documents[0].id


    @classmethod
    def tearDownClass(cls):
        """Clean up the created vector collection and document."""
        cls.vector_client.delete_document(cls.collection_id, cls.document_id)

        cls.vector_client.delete_collection(cls.collection_id)


    def test_01_get_data_repositories(self):
        """Verify that the test collection appears as a repository in Retrieval API."""
        response = self.retrieval_client.get_data_repositories()
        self.assertIsInstance(response, DataRepositories)
        created_repo = None
        for r in response.resources:
            if r.id == self.__class__.collection_id:
                created_repo = r
                break

        self.assertIsNotNone(created_repo)
        self.assertEqual(created_repo.title, self.collection_title)
        self.assertEqual(created_repo.type, "vector")

        metadata = {m.key: m.value for m in created_repo.metadata}
        self.assertEqual(metadata["purpose"], ["retrieval-test"])
        self.assertEqual(metadata["source"], ["integration"])

        help_repo = None
        for r in response.resources:
            if r.type == "help.sap.com":
                help_repo = r
                break

        self.assertIsNotNone(help_repo)
        self.assertEqual(help_repo.title, "SAP Help Portal - help.sap.com")
        self.assertEqual(help_repo.metadata, [])
        self.assertEqual(help_repo.type, "help.sap.com")

    def test_02_get_data_repository_by_id(self):
        """Get repository details and verify consistency with the created collection."""
        response = self.retrieval_client.get_data_repository_by_id(self.__class__.collection_id)

        self.assertIsInstance(response, DataRepository)

        self.assertEqual(response.id, self.__class__.collection_id)
        self.assertEqual(response.title, self.collection_title)
        self.assertEqual(response.type, "vector")

        metadata = {m.key: m.value for m in response.metadata}
        self.assertIn("purpose", metadata)
        self.assertIn("source", metadata)
        self.assertEqual(metadata["purpose"], ["retrieval-test"])
        self.assertEqual(metadata["source"], ["integration"])

    def test_03_search_retrieval(self):
        """Perform a retrieval search in the created vector repository and verify content consistency."""
        search_input = RetrievalSearchInput(
            query="What is Joule?",
            filters=[
                RetrievalSearchFilter(
                    id="string",
                    dataRepositoryType="vector",
                    searchConfiguration=RetrievalSearchConfiguration(),
                    dataRepositories=[self.__class__.collection_id],
                    documentMetadata=[
                        RetrievalSearchDocumentKeyValueListPair(
                            key="url",
                            value=["http://retrieval-test.com"],
                            selectMode=["ignoreIfKeyAbsent"],
                        )
                    ],
                )
            ],
        )

        response = self.retrieval_client.search(search_input)

        self.assertIsInstance(response, RetrievalSearchResults)
        self.assertTrue(response.results)

        filter_result = response.results[0]
        self.assertEqual(filter_result.filterId, "string")
        self.assertTrue(filter_result.results)

        repo = filter_result.results[0].dataRepository
        self.assertEqual(repo.id, self.__class__.collection_id)
        self.assertEqual(repo.title, self.collection_title)

        metadata = {m.key: m.value for m in repo.metadata}
        self.assertEqual(metadata.get("purpose"), ["retrieval-test"])
        self.assertEqual(metadata.get("source"), ["integration"])

        document = repo.documents[0]
        metadata_dict = {m.key: m.value for m in document.metadata}
        self.assertEqual(metadata_dict.get("url"), ["http://retrieval-test.com"])
        self.assertTrue(document.chunks)

        chunk = document.chunks[0]
        self.assertIn("Joule", chunk.content)

        chunk_metadata = {m.key: m.value for m in chunk.metadata}
        self.assertIn("index", chunk_metadata)
