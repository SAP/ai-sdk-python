import requests
from gen_ai_hub.document_grounding.models.vector import (
    Collection,
    CollectionsListResponse,
    CollectionCreateRequest,
    CollectionCreatedResponse,
    CollectionDeletedResponse,
    CollectionPendingResponse,
    DocumentsCreateRequest,
    DocumentsUpdateRequest,
    DocumentsListResponse,
    Document,
    DocumentsResponse,
    VectorKeyValueListPair,
    TextOnlyBaseChunk,
    BaseDocument,
    VectorSearchResults,
    VectorPerFilterSearchResult,
    DocumentsChunk,
    DocumentOutput,
    DocumentWithoutChunks,
    VectorChunk,
    TextSearchRequest,
    VectorSearchFilter,
    VectorSearchConfiguration,
    VectorSearchDocumentKeyValueListPair,

)

"""Document Grounding Vector API test constants"""

PATH_VECTOR_API_ = "/lm/document-grounding/vector"
COLLECTION_ID = "84f4f74b-8df9-4c73-8f2d-5729b24dd6eb"
DOCUMENT_ID = "0fb9878d-72fe-4267-8f4b-f68947729aab"

# --- Collections ---
COLLECTION = Collection(
    id=COLLECTION_ID,
    title="test-collection",
    embeddingConfig={"modelName": "text-embedding-3-large"},
    metadata=[VectorKeyValueListPair(key="purpose", value=["testing"])]
)

COLLECTIONS_LIST_RESPONSE = CollectionsListResponse(count=1, resources=[COLLECTION])

COLLECTION_CREATE_REQUEST = CollectionCreateRequest(
    title="test-collection",
    embeddingConfig={"modelName": "text-embedding-3-large"},
    metadata=[VectorKeyValueListPair(key="purpose", value=["testing"])]
)

COLLECTION_CREATED_RESPONSE = CollectionCreatedResponse(collectionUrl=f"{PATH_VECTOR_API_}/collections/{COLLECTION_ID}")
COLLECTION_PENDING_RESPONSE = CollectionPendingResponse(location=f"{PATH_VECTOR_API_}/collections/{COLLECTION_ID}/status")
COLLECTION_DELETED_RESPONSE = CollectionDeletedResponse(collectionUrl=f"{PATH_VECTOR_API_}/collections/{COLLECTION_ID}")

# --- Documents ---
CHUNK_1 = TextOnlyBaseChunk(
    content="This is a test chunk",
    metadata=[VectorKeyValueListPair(key="index", value=["1"])]
)
CHUNK_2 = TextOnlyBaseChunk(
    content="Another test chunk",
    metadata=[VectorKeyValueListPair(key="index", value=["2"])]
)

VECTOR_CHUNK_1 = VectorChunk(
    id="chunk-1",
    content="This is a test chunk",
    metadata=[VectorKeyValueListPair(key="index", value=["1"])]
)

VECTOR_CHUNK_2 = VectorChunk(
    id="chunk-2",
    content="Another test chunk",
    metadata=[VectorKeyValueListPair(key="index", value=["2"])]
)

BASE_DOCUMENT = BaseDocument(
    chunks=[CHUNK_1, CHUNK_2],
    metadata=[VectorKeyValueListPair(key="url", value=["http://example.com"])]
)

DOCUMENT = Document(
    id=DOCUMENT_ID,
    chunks=[CHUNK_1, CHUNK_2],
    metadata=[VectorKeyValueListPair(key="url", value=["http://example.com"])]
)

DOCUMENTS_CREATE_REQUEST = DocumentsCreateRequest(documents=[BASE_DOCUMENT])
DOCUMENTS_UPDATE_REQUEST = DocumentsUpdateRequest(documents=[DOCUMENT])

DOCUMENT_WITHOUT_CHUNKS = DocumentWithoutChunks(
    id="0fb9878d-72fe-4267-8f4b-f68947729aab",
    metadata=[VectorKeyValueListPair(key="url", value=["http://example.com"])]
)

DOCUMENTS_LIST_RESPONSE = DocumentsListResponse(documents=[DOCUMENT_WITHOUT_CHUNKS])
DOCUMENTS_RESPONSE = DocumentsResponse(count=1, resources=[DOCUMENT_WITHOUT_CHUNKS])

# --- Vector Search ---
VECTOR_SEARCH_REQUEST = TextSearchRequest(
    query="is Joule an AI Copilot?",
    filters=[
        VectorSearchFilter(
            id="filter-001",
            collectionIds=["84f4f74b-8df9-4c73-8f2d-5729b24dd6eb"],
            configuration=VectorSearchConfiguration(
                maxChunkCount=5,
                maxDocumentCount=2
            ),
            collectionMetadata=[
                VectorKeyValueListPair(key="domain", value=["sap", "ai"]),
                VectorKeyValueListPair(key="environment", value=["production"])
            ],
            documentMetadata=[
                VectorSearchDocumentKeyValueListPair(
                    key="author",
                    value=["SAP Labs"],
                    selectMode=["INCLUDE"]
                )
            ],
            chunkMetadata=[
                VectorKeyValueListPair(key="language", value=["en"]),
                VectorKeyValueListPair(key="topic", value=["copilot"])
            ]
        )
    ]
)
VECTOR_SEARCH_RESPONSE = VectorSearchResults(
    results=[
        VectorPerFilterSearchResult(
            filterId="filter-001",
            results=[
                DocumentsChunk(
                    id="84f4f74b-8df9-4c73-8f2d-5729b24dd6eb",
                    title="SAP Joule Overview",
                    metadata=[
                        VectorKeyValueListPair(key="domain", value=["sap", "ai"]),
                        VectorKeyValueListPair(key="environment", value=["production"])
                    ],
                    documents=[
                        DocumentOutput(
                            id="0fb9878d-72fe-4267-8f4b-f68947729aab",
                            metadata=[
                                VectorKeyValueListPair(key="author", value=["SAP Labs"]),
                                VectorKeyValueListPair(key="language", value=["en"])
                            ],
                            chunks=[
                                VectorChunk(
                                    id="chunk-001",
                                    content="Joule is the AI copilot that understands your business context deeply.",
                                    metadata=[
                                        VectorKeyValueListPair(key="topic", value=["copilot"]),
                                        VectorKeyValueListPair(key="index", value=["1"])
                                    ]
                                ),
                                VectorChunk(
                                    id="chunk-002",
                                    content="It integrates across SAP systems to streamline workflows and enhance productivity.",
                                    metadata=[
                                        VectorKeyValueListPair(key="topic", value=["copilot"]),
                                        VectorKeyValueListPair(key="index", value=["2"])
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

# --- Common Responses ---
RESPONSE_202 = requests.Response()
RESPONSE_202.status_code = 202

RESPONSE_204 = requests.Response()
RESPONSE_204.status_code = 204
