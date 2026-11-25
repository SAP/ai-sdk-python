"""Pydantic models for Retrieval API.

This module defines data models for the Retrieval API, which enables querying
and retrieving relevant content from configured data repositories (vector stores
and external document sources).

Model categories:
    - Data repository models (repository information and metadata)
    - Chunk and document models (content structure)
    - Search filter and configuration models (query parameters)
    - Search input and result models (request/response structures)

The Retrieval API supports semantic search combined with metadata filtering
for precise content retrieval across multiple repository types.
"""
from typing import List, Optional, Union, Literal
from pydantic import Field

from gen_ai_hub._base_model import SdkBaseModel

# --- Common Key/Value models ---

class RetrievalKeyValueListPair(SdkBaseModel):
    key: str
    value: List[str]


class RetrievalDocumentKeyValueListPair(RetrievalKeyValueListPair):
    matchMode: Optional[str]



class RetrievalSearchDocumentKeyValueListPair(SdkBaseModel):
    key: str
    value: List[str]
    selectMode: Optional[List[str]] = None


# --- Retrieval Chunk and Document models ---

class RetrievalChunk(SdkBaseModel):
    id: str
    content: str
    metadata: Optional[List[RetrievalKeyValueListPair]] = Field(default_factory=list)


class RetrievalDocument(SdkBaseModel):
    id: str
    metadata: Optional[List[RetrievalDocumentKeyValueListPair]] = Field(default_factory=list)
    chunks: List[RetrievalChunk]


# --- Data Repository models ---

DataRepositoryType = Union[
    Literal["vector", "help.sap.com"],
    str
]


class DataRepository(SdkBaseModel):
    id: str
    title: str
    type: DataRepositoryType
    metadata: Optional[List[RetrievalKeyValueListPair]] = Field(default_factory=list)


class DataRepositoryWithDocuments(SdkBaseModel):
    id: str
    title: str
    metadata: Optional[List[RetrievalKeyValueListPair]] = Field(default_factory=list)
    documents: List[RetrievalDocument]


# --- Retrieval Filter and Configuration models ---

class RetrievalSearchConfiguration(SdkBaseModel):
    maxChunkCount: Optional[int] = None
    maxDocumentCount: Optional[int] = None


class RetrievalSearchFilter(SdkBaseModel):
    id: str
    dataRepositoryType:  DataRepositoryType
    searchConfiguration: Optional[RetrievalSearchConfiguration] = Field(default_factory=RetrievalSearchConfiguration)
    dataRepositories: Optional[List[str]] = Field(default_factory=list)
    dataRepositoryMetadata: Optional[List[RetrievalKeyValueListPair]] = Field(default_factory=list)
    documentMetadata: Optional[List[RetrievalSearchDocumentKeyValueListPair]] = Field(default_factory=list)
    chunkMetadata: Optional[List[RetrievalKeyValueListPair]] = Field(default_factory=list)


# --- Retrieval Search Input and Results ---

class RetrievalSearchInput(SdkBaseModel):
    query: str
    filters: List[RetrievalSearchFilter]


class RetrievalDataRepositorySearchResult(SdkBaseModel):
    dataRepository: DataRepositoryWithDocuments


class RetrievalPerFilterSearchResult(SdkBaseModel):
    filterId: str
    results: List[RetrievalDataRepositorySearchResult] = Field(default_factory=list)


class RetrievalPerFilterSearchResultError(SdkBaseModel):
    message: str


class RetrievalPerFilterSearchResultWithError(SdkBaseModel):
    filterId: str
    error: RetrievalPerFilterSearchResultError


class RetrievalSearchResults(SdkBaseModel):
    results: List[Union[RetrievalPerFilterSearchResult, RetrievalPerFilterSearchResultWithError]]


# --- List & Single Repository responses ---

class DataRepositories(SdkBaseModel):
    count: Optional[int] = None
    resources: List[DataRepository]

