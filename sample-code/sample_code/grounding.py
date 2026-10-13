from fastapi import Body, Query
from pydantic import BaseModel, Field

from gen_ai_hub.document_grounding.client import (
    PipelineAPIClient,
    RetrievalAPIClient,
    VectorAPIClient,
)
from gen_ai_hub.document_grounding.models.retrieval import (
    RetrievalSearchConfiguration,
    RetrievalSearchFilter,
    RetrievalSearchInput,
)
from gen_ai_hub.document_grounding.models.vector import (
    BaseDocument,
    CollectionCreateRequest,
    DocumentsCreateRequest,
    EmbeddingConfig,
    TextOnlyBaseChunk,
    VectorKeyValueListPair,
)


class DocumentChunk(BaseModel):
    content: str
    topic: str
    language: str = "en"


class CreateDocumentsBody(BaseModel):
    documents: list[DocumentChunk] = Field(
        default=[
            DocumentChunk(
                content="SAP BTP provides cloud-native platform services for building enterprise applications.",
                topic="BTP",
            ),
            DocumentChunk(
                content="HANA Vector Store enables semantic search over large document collections using embeddings.",
                topic="HANA",
            ),
        ],
        description="List of documents to ingest. Each document has content, topic, and language.",
    )


def get_collections():
    """List all vector collections available to the tenant."""
    client = VectorAPIClient()
    return client.get_collections()


def create_collection(
    title: str = Query(default="sample-collection", description="Title for the new collection."),
    embedding_model: str = Query(default="text-embedding-3-small", description="Embedding model to use for this collection."),
):
    """
    Create a new vector collection.

    Provide `title` and `embedding_model` to customise the collection.
    Defaults create a collection named 'sample-collection' with text-embedding-3-small.
    """
    client = VectorAPIClient()
    return client.create_collection(
        CollectionCreateRequest(
            title=title,
            embeddingConfig=EmbeddingConfig(modelName=embedding_model),
            metadata=[VectorKeyValueListPair(key="source", value=["sample-code"])],
        )
    )


def delete_collection(collection_id: str):
    """Delete a collection by its ID."""
    client = VectorAPIClient()
    return client.delete_collection(collection_id)


def create_documents(
    collection_id: str,
    body: CreateDocumentsBody = Body(default=None),
):
    """
    Add documents to an existing collection.

    Omit the request body to ingest the two built-in SAP BTP / HANA sample documents.
    Provide your own documents list to ingest custom content.
    """
    if body is None:
        body = CreateDocumentsBody()
    client = VectorAPIClient()
    return client.create_documents(
        collection_id,
        DocumentsCreateRequest(
            documents=[
                BaseDocument(
                    chunks=[
                        TextOnlyBaseChunk(
                            content=doc.content,
                            metadata=[VectorKeyValueListPair(key="language", value=[doc.language])],
                        )
                    ],
                    metadata=[VectorKeyValueListPair(key="topic", value=[doc.topic])],
                )
                for doc in body.documents
            ]
        ),
    )


def get_pipelines():
    """List all document vectorization pipelines configured for the tenant."""
    client = PipelineAPIClient()
    return client.get_pipelines()


def retrieval_documents(
    query: str = Query(
        default="What are the key features of SAP BTP?",
        description="Natural language query to search the vector knowledge base.",
    ),
    max_chunks: int = Query(default=3, ge=1, le=20, description="Maximum number of chunks to retrieve."),
):
    """
    Retrieve relevant document chunks by semantic similarity to `query`.

    Searches across all vector data repositories in the tenant.
    """
    client = RetrievalAPIClient()
    return client.search(
        RetrievalSearchInput(
            query=query,
            filters=[
                RetrievalSearchFilter(
                    id="filter-1",
                    dataRepositoryType="vector",
                    dataRepositories=["*"],
                    searchConfiguration=RetrievalSearchConfiguration(maxChunkCount=max_chunks),
                )
            ],
        )
    )
