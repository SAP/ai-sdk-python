from fastapi import Query

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


def get_collections():
    """
    List all vector collections available to the tenant.

    Returns:
        JSON object containing the list of collections.
    """
    client = VectorAPIClient()
    return client.get_collections()


def create_collection():
    """
    Create a new vector collection with a text-embedding model.

    Returns:
        JSON object containing the ID of the created collection.
    """
    client = VectorAPIClient()
    return client.create_collection(
        CollectionCreateRequest(
            title="sample-collection",
            embeddingConfig=EmbeddingConfig(modelName="text-embedding-3-large"),
            metadata=[VectorKeyValueListPair(key="source", value=["sample-code"])],
        )
    )


def delete_collection(collection_id: str):
    """
    Delete a collection by its ID.

    Args:
        collection_id: The ID of the collection to delete.

    Returns:
        HTTP response confirming deletion with HTTP status code 204.
    """
    client = VectorAPIClient()
    return client.delete_collection(collection_id)


def create_documents(collection_id: str):
    """
    Add two sample documents with text chunks to an existing collection.

    Args:
        collection_id: The ID of the collection to add documents to.

    Returns:
        JSON object containing the created document IDs.
    """
    client = VectorAPIClient()
    return client.create_documents(
        collection_id,
        DocumentsCreateRequest(
            documents=[
                BaseDocument(
                    chunks=[
                        TextOnlyBaseChunk(
                            content="SAP BTP provides cloud-native platform services for building enterprise applications.",
                            metadata=[VectorKeyValueListPair(key="language", value=["en"])],
                        )
                    ],
                    metadata=[VectorKeyValueListPair(key="topic", value=["BTP"])],
                ),
                BaseDocument(
                    chunks=[
                        TextOnlyBaseChunk(
                            content="HANA Vector Store enables semantic search over large document collections using embeddings.",
                            metadata=[VectorKeyValueListPair(key="language", value=["en"])],
                        )
                    ],
                    metadata=[VectorKeyValueListPair(key="topic", value=["HANA"])],
                ),
            ]
        ),
    )


def get_pipelines():
    """
    List all document vectorization pipelines configured for the tenant.

    Returns:
        JSON object containing the list of pipelines with their IDs and types.
    """
    client = PipelineAPIClient()
    return client.get_pipelines()


def retrieval_documents(
    query: str = "What are the key features of SAP BTP?",
    data_repository_type: str = "vector",
    data_repositories: list[str] = Query(default=["*"]),
):
    """
    Retrieve documents across data repositories.

    Args:
        query: Search query.
        data_repository_type: Type of data repository.
        data_repositories: List of data repository IDs to search in.

    Returns:
        Search results.
    """
    client = RetrievalAPIClient()
    return client.search(
        RetrievalSearchInput(
            query=query,
            filters=[
                RetrievalSearchFilter(
                    id="filter-1",
                    dataRepositoryType=data_repository_type,
                    dataRepositories=data_repositories,
                    searchConfiguration=RetrievalSearchConfiguration(maxChunkCount=1),
                )
            ],
        )
    )
