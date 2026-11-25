"""Pydantic models for Vector API.

This module defines data models for the Vector API, which provides management
and search capabilities for vector-based document collections.

Model categories:
    - Collection models (collection configuration and management)
    - Document and chunk models (content structure with embeddings)
    - Embedding configuration models (embedding model settings)
    - Search models (semantic search requests and results)
    - Status models (collection creation/deletion tracking)

The Vector API enables semantic search across document collections using
vector embeddings for similarity-based retrieval.
"""
from typing import List, Optional, Annotated, Literal
from pydantic import Field

from gen_ai_hub._base_model import SdkBaseModel

# --- Models for Vector API ---

# --- Common key-value metadata pair ---
class VectorKeyValueListPair(SdkBaseModel):
    key: str
    value: List[str]


# --- Embedding Config ---
class EmbeddingConfig(SdkBaseModel):
    modelName: Optional[str] = Field(default="text-embedding-3-large")


# --- Collection Models ---
class CollectionCreateRequest(SdkBaseModel):
    title: Optional[str] = None
    embeddingConfig: EmbeddingConfig
    metadata: Optional[List[VectorKeyValueListPair]] = []


class Collection(SdkBaseModel):
    id: str
    title: Optional[str] = None
    embeddingConfig: EmbeddingConfig
    metadata: Optional[List[VectorKeyValueListPair]] = []


class CollectionsListResponse(SdkBaseModel):
    count: Optional[int] = None
    resources: List[Collection]


# --- Chunk and Document Models ---
class TextOnlyBaseChunk(SdkBaseModel):
    content: str
    metadata: Optional[List[VectorKeyValueListPair]] = []


class BaseDocument(SdkBaseModel):
    chunks: List[TextOnlyBaseChunk]
    metadata: List[VectorKeyValueListPair]


class DocumentWithoutChunks(SdkBaseModel):
    id: str
    metadata: List[VectorKeyValueListPair]


class Document(BaseDocument):
    id: str


class DocumentsCreateRequest(SdkBaseModel):
    documents: List[BaseDocument]


class DocumentsUpdateRequest(SdkBaseModel):
    documents: List[Document]


class DocumentsListResponse(SdkBaseModel):
    documents: List[DocumentWithoutChunks]


class DocumentsResponse(SdkBaseModel):
    count: Optional[int] = None
    resources: List[DocumentWithoutChunks]


# --- Collection Status Models ---

class CollectionCreatedResponse(SdkBaseModel):
    collectionURL: str = Field(alias="collectionUrl")
    status: Literal["CREATED"] = "CREATED"


class CollectionDeletedResponse(SdkBaseModel):
    collectionURL: str = Field(alias="collectionUrl")
    status: Literal["DELETED"] = "DELETED"


class CollectionPendingResponse(SdkBaseModel):
    Location: str = Field(alias="location")
    status: Literal["PENDING"] = "PENDING"


CollectionCreationStatusResponse = Annotated[
    CollectionCreatedResponse | CollectionPendingResponse,
    Field(discriminator="status")
]

CollectionDeletionStatusResponse = Annotated[
    CollectionDeletedResponse | CollectionPendingResponse,
    Field(discriminator="status")
]

# --- Vector Search Models ---
class VectorSearchConfiguration(SdkBaseModel):
    maxChunkCount: Optional[int] = None
    maxDocumentCount: Optional[int] = None


class VectorSearchDocumentKeyValueListPair(SdkBaseModel):
    key: str
    value: List[str]
    selectMode: Optional[List[str]] = None


class VectorSearchFilter(SdkBaseModel):
    id: str
    collectionIds: List[str]
    configuration: VectorSearchConfiguration
    collectionMetadata: Optional[List[VectorKeyValueListPair]] = []
    documentMetadata: Optional[List[VectorSearchDocumentKeyValueListPair]] = []
    chunkMetadata: Optional[List[VectorKeyValueListPair]] = []


class TextSearchRequest(SdkBaseModel):
    query: str
    filters: List[VectorSearchFilter]


# --- Vector Search Results ---
class VectorChunk(SdkBaseModel):
    id: str
    content: str
    metadata: Optional[List[VectorKeyValueListPair]] = []


class DocumentOutput(SdkBaseModel):
    id: str
    metadata: Optional[List[VectorKeyValueListPair]] = []
    chunks: List[VectorChunk]


class DocumentsChunk(SdkBaseModel):
    id: str
    title: str
    metadata: Optional[List[VectorKeyValueListPair]] = []
    documents: List[DocumentOutput]


class VectorPerFilterSearchResult(SdkBaseModel):
    filterId: str
    results: List[DocumentsChunk]


class VectorSearchResults(SdkBaseModel):
    results: List[VectorPerFilterSearchResult]
