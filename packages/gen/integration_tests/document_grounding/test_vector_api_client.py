import unittest
from typing import cast
import requests.status_codes

from .. import get_random_string
from gen_ai_hub import GenAIHubProxyClient
from gen_ai_hub.proxy import get_proxy_client
from gen_ai_hub.document_grounding.clients.vector_api_client import VectorAPIClient
from gen_ai_hub.document_grounding.models.vector import (
    Collection,
    CollectionCreateRequest,
    EmbeddingConfig,
    VectorKeyValueListPair,
    DocumentsCreateRequest,
    BaseDocument,
    TextOnlyBaseChunk,
    DocumentsUpdateRequest,
    Document,
    TextSearchRequest,
    VectorSearchFilter,
    VectorSearchConfiguration,
    VectorSearchDocumentKeyValueListPair,
)
from integration_tests.test_helpers import retry_on_429_or_503_class


@retry_on_429_or_503_class()
class TestVectorAPIIntegration(unittest.TestCase):
    """
    Integration test suite for the Vector API.

    Covers:
      - Collections
      - Collection statuses
      - Documents CRUD
      - Search queries

    Prerequisites:
      - Resource group with Document Grounding API enabled.
      - Valid Vector Store and secrets.
    """

    @classmethod
    def setUpClass(cls):
        cls.proxy_client = cast(GenAIHubProxyClient, get_proxy_client())
        cls.client = VectorAPIClient(proxy_client=cls.proxy_client)
        cls.collection_id = None
        cls.document_id = None


    def test_integration(self):
        # --- Collections ---

        # Create a vector collection.
        self.collection_title = f"test-canary-collection-{get_random_string()}"
        request = CollectionCreateRequest(
            title=self.collection_title,
            embeddingConfig=EmbeddingConfig(modelName="text-embedding-3-large"),
            metadata=[
                VectorKeyValueListPair(key="purpose", value=["demonstration"]),
                VectorKeyValueListPair(key="a-random-key", value=["hello world!"]),
            ],
        )
        response = self.client.create_collection(request)

        self.assertEqual(response.status_code, requests.status_codes.codes.ACCEPTED)

        # Retrieve all collections and validate the last created collection data.
        response = self.client.get_collections()
        self.assertGreaterEqual(response.count, 0)

        self.assertTrue(response.resources)

        test_collection: Collection = None
        for res in response.resources:
            if res.title == self.collection_title:
                test_collection = res
        self.assertIsNotNone(test_collection)
        self.__class__.collection_id = test_collection.id

        self.assertIn(self.collection_title, test_collection.title)

        self.assertEqual(
            test_collection.embeddingConfig.modelName,
            "text-embedding-3-large",
        )

        metadata_keys = {m.key: m.value for m in (test_collection.metadata or [])}
        self.assertIn("purpose", metadata_keys)
        self.assertIn("a-random-key", metadata_keys)

        self.assertEqual(metadata_keys["purpose"], ["demonstration"])
        self.assertEqual(metadata_keys["a-random-key"], ["hello world!"])

        self.assertTrue(self.__class__.collection_id)

        # Fetch details of a specific collection by ID and verify all expected fields.
        self.assertTrue(self.__class__.collection_id)

        response = self.client.get_collection_by_id(self.__class__.collection_id)

        self.assertEqual(response.id, self.__class__.collection_id)
        self.assertEqual(response.title, self.collection_title)
        self.assertEqual(response.embeddingConfig.modelName, "text-embedding-3-large")

        expected_metadata = {
            "purpose": ["demonstration"],
            "a-random-key": ["hello world!"]
        }

        metadata_dict = {m.key: m.value for m in response.metadata}

        for key, expected_value in expected_metadata.items():
            self.assertIn(key, metadata_dict)
            self.assertEqual(metadata_dict[key], expected_value)

        # --- Collection statuses ---

        # Check async creation status (CREATED/PENDING).
        self.assertTrue(self.__class__.collection_id)
        response = self.client.get_collection_creation_status(self.__class__.collection_id)

        self.assertTrue(response.status)


        # --- Documents ---

        # Insert new documents into the collection and verify creation response.
        self.assertTrue(self.__class__.collection_id)

        document = BaseDocument(
            metadata=[VectorKeyValueListPair(key="url", value=["http://hello.com", "123"])],
            chunks=[
                TextOnlyBaseChunk(
                    content=(
                        "Joule is the AI copilot that truly understands your business. "
                        "Joule revolutionizes how you interact with your SAP systems."
                    ),
                    metadata=[VectorKeyValueListPair(key="index", value=["1"])],
                ),
                TextOnlyBaseChunk(
                    content=(
                        "It enables the Intelligent Enterprise, guiding you through SAP content discovery "
                        "and providing transparent access to relevant processes."
                    ),
                    metadata=[VectorKeyValueListPair(key="index", value=["2"])],
                ),
            ],
        )

        request = DocumentsCreateRequest(documents=[document])
        response = self.client.create_documents(self.__class__.collection_id, request)

        self.assertTrue(response.documents)
        created_doc = response.documents[0]

        self.assertIsNotNone(created_doc.id)
        self.assertEqual(len(created_doc.metadata), 1)

        metadata = created_doc.metadata[0]
        self.assertEqual(metadata.key, "url")
        self.assertEqual(metadata.value, ["http://hello.com", "123"])

        self.__class__.document_id = created_doc.id

        # Retrieve all documents in a collection and verify their structure.
        self.assertTrue(self.__class__.collection_id)

        response = self.client.get_documents(self.__class__.collection_id)

        self.assertGreaterEqual(response.count or 0, 1)
        self.assertTrue(response.resources)

        for doc in response.resources:
            self.assertIsNotNone(doc.id)
            self.assertTrue(doc.metadata)
            metadata = doc.metadata[0]
            self.assertEqual(metadata.key, "url")
            self.assertEqual(metadata.value, ["http://hello.com", "123"])

        # Get a document by its ID and verify all content and metadata.
        self.assertTrue(self.__class__.collection_id)
        self.assertTrue(self.__class__.document_id)

        response = self.client.get_document_by_id(self.__class__.collection_id, self.__class__.document_id)

        self.assertEqual(response.id, self.__class__.document_id)
        self.assertTrue(response.metadata)
        self.assertTrue(response.chunks)
        self.assertGreaterEqual(len(response.chunks), 2)

        metadata = {m.key: m.value for m in response.metadata}
        self.assertIn("url", metadata)
        self.assertEqual(metadata["url"], ["http://hello.com", "123"])

        first_chunk = response.chunks[0]
        second_chunk = response.chunks[1]

        self.assertIn("Joule is the AI copilot", first_chunk.content)
        self.assertIn("It enables the Intelligent Enterprise", second_chunk.content)

        chunk_metadata_keys = [m.key for m in first_chunk.metadata]
        self.assertIn("index", chunk_metadata_keys)

        # Update an existing document and verify that changes persist.
        self.assertTrue(self.__class__.collection_id)
        self.assertTrue(self.__class__.document_id)

        updated_doc = Document(
            id=self.__class__.document_id,
            metadata=[VectorKeyValueListPair(key="url", value=["http://hello1.com"])],
            chunks=[
                TextOnlyBaseChunk(
                    content=(
                        "Joule is not the AI copilot that truly understands your business. "
                        "Joule revolutionizes how you interact with your SAP business systems, making every touchpoint count and every task simpler."
                    ),
                    metadata=[VectorKeyValueListPair(key="index", value=["1"])],
                ),
                TextOnlyBaseChunk(
                    content=(
                        "It enables the companion of the Intelligent Enterprise, guiding you through content discovery within SAP Ecosystem, "
                        "and giving a transparent role-based access to the relevant processes from everywhere. "
                        "This is the one assistant experience, a unified and delightful user experience across SAP’s solution portfolio."
                    ),
                    metadata=[VectorKeyValueListPair(key="index", value=["2"])],
                ),
            ],
        )

        request = DocumentsUpdateRequest(documents=[updated_doc])
        response = self.client.update_documents(self.__class__.collection_id, request)

        self.assertTrue(response.documents)
        updated_metadata = response.documents[0].metadata[0]
        self.assertEqual(updated_metadata.key, "url")
        self.assertEqual(updated_metadata.value, ["http://hello1.com"])

        # Follow-up check — ensure data is persisted via GET
        fetched_doc = self.client.get_document_by_id(self.__class__.collection_id, self.__class__.document_id)

        self.assertEqual(fetched_doc.id, self.__class__.document_id)
        fetched_metadata = {m.key: m.value for m in fetched_doc.metadata}
        self.assertIn("url", fetched_metadata)
        self.assertEqual(fetched_metadata["url"], ["http://hello1.com"])

        first_chunk = fetched_doc.chunks[0]
        second_chunk = fetched_doc.chunks[1]

        self.assertIn("not the AI copilot", first_chunk.content)
        self.assertIn("It enables the companion of the Intelligent Enterprise", second_chunk.content)

        # --- Search ---

        # Perform a semantic vector search and verify results and data consistency.
        self.assertTrue(self.__class__.collection_id)

        request = TextSearchRequest(
            query="is Joule an AI Copilot?",
            filters=[
                VectorSearchFilter(
                    id="string",
                    collectionIds=[self.__class__.collection_id],
                    configuration=VectorSearchConfiguration(),
                    collectionMetadata=[],
                    documentMetadata=[
                        VectorSearchDocumentKeyValueListPair(
                            key="url",
                            value=["http://hello1.com"],
                            selectMode=["ignoreIfKeyAbsent"],
                        )
                    ],
                    chunkMetadata=[],
                )
            ],
        )

        response = self.client.search(request)

        self.assertTrue(response.results)
        filter_result = response.results[0]
        self.assertEqual(filter_result.filterId, "string")
        self.assertTrue(filter_result.results)

        collection_result = filter_result.results[0]
        self.assertEqual(collection_result.title, self.collection_title)
        self.assertTrue(collection_result.metadata)
        self.assertTrue(collection_result.documents)

        document_result = collection_result.documents[0]
        metadata_dict = {m.key: m.value for m in document_result.metadata}
        self.assertIn("url", metadata_dict)
        self.assertEqual(metadata_dict["url"], ["http://hello1.com"])

        self.assertTrue(document_result.chunks)
        self.assertTrue(any("Joule" in chunk.content for chunk in document_result.chunks))

        for chunk in document_result.chunks:
            self.assertIsInstance(chunk.id, str)
            self.assertIsInstance(chunk.content, str)
            self.assertTrue(any(m.key == "index" for m in chunk.metadata))

        # --- Cleanup ---

        # Delete a document (204 No Content).
        self.assertTrue(self.__class__.collection_id)
        self.assertTrue(self.__class__.document_id)
        response = self.client.delete_document(self.__class__.collection_id, self.__class__.document_id)
        self.assertEqual(response.status_code, requests.status_codes.codes.NO_CONTENT)

        # Delete a collection (204 No Content).
        self.assertTrue(self.__class__.collection_id)
        response = self.client.delete_collection(self.__class__.collection_id)
        self.assertEqual(response.status_code, requests.status_codes.codes.NO_CONTENT)

        # Verify deletion status after deletion.
        self.assertTrue(self.__class__.collection_id)
        response = self.client.get_collection_deletion_status(self.__class__.collection_id)
        self.assertIn(response.status, ["DELETED", "PENDING"])
