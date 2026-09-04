from ai_core_sdk.ai_core_v2_client import AICoreV2Client
from gen_ai_hub.document_grounding_generation import (
    GroundingApiClient,
    CollectionRequest,
    DataRepositoryType,
    EmbeddingConfig,
    FiltersInner,
    PipelinesApi,
    RetrievalApi,
    RetrievalSearchConfiguration,
    RetrievalSearchFilter,
    RetrievalSearchInput,
    VectorApi,
)

RESOURCE_GROUP = "default"


def _client() -> GroundingApiClient:
    return GroundingApiClient(AICoreV2Client.from_env())


async def create_collection():
    """
    Create a new vector collection through the Document Grounding Vector API.

    Returns:
        JSON object containing the created collection details.
    """
    client = _client()
    await VectorApi(client).create_collection(
        ai_resource_group=RESOURCE_GROUP,
        collection_request=CollectionRequest(
            title="my-collection",
            embedding_config=EmbeddingConfig(model_name="text-embedding-3-small"),
        ),
    )
    return {"result": "collection creation initiated"}


async def get_all_pipelines():
    """
    List all document grounding pipelines through the Document Grounding Pipelines API.

    Returns:
        JSON object containing the list of pipelines.
    """
    client = _client()
    result = await PipelinesApi(client).get_all_pipelines(
        ai_resource_group=RESOURCE_GROUP,
    )
    return {"result": result.to_dict()}


async def retrieval_search():
    """
    Search across data repositories through the Document Grounding Retrieval API.

    Returns:
        JSON object containing the search results.
    """
    client = _client()
    result = await RetrievalApi(client).search(
        ai_resource_group=RESOURCE_GROUP,
        retrieval_search_input=RetrievalSearchInput(
            query="What is SAP BTP?",
            filters=[
                FiltersInner(RetrievalSearchFilter(
                    id="my-data-repository-id",
                    data_repository_type=DataRepositoryType.VECTOR,
                    search_configuration=RetrievalSearchConfiguration(
                        max_chunk_count=5,
                    ),
                ))
            ],
        ),
    )
    return {"result": result.to_dict()}
