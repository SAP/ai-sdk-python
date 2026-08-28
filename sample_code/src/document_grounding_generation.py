from ai_core_sdk.ai_core_v2_client import AICoreV2Client
from gen_ai_hub.document_grounding_generation import (
    GroundingApiClient,
    CollectionRequest,
    EmbeddingConfig,
    PipelinesApi,
    RetrievalApi,
    RetrievalSearchConfiguration,
    RetrievalSearchFilter,
    RetrievalSearchInput,
    TextSearchRequest,
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
    result = await VectorApi(client).create_collection(
        collection_request=CollectionRequest(
            title="my-collection",
            embeddingConfig=EmbeddingConfig(modelName="text-embedding-3-small"),
        ),
        header_parameters={"AI-Resource-Group": RESOURCE_GROUP},
    )
    return {"result": result.to_dict()}


async def get_all_pipelines():
    """
    List all document grounding pipelines through the Document Grounding Pipelines API.

    Returns:
        JSON object containing the list of pipelines.
    """
    client = _client()
    result = await PipelinesApi(client).get_all_pipelines(
        header_parameters={"AI-Resource-Group": RESOURCE_GROUP},
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
        text_search_request=TextSearchRequest(
            query="What is SAP BTP?",
            filters=[
                RetrievalSearchFilter(
                    id="my-data-repository-id",
                    search_configuration=RetrievalSearchConfiguration(
                        max_chunk_count=5,
                    ),
                )
            ],
            search_configuration=RetrievalSearchInput(
                max_chunk_count=10,
            ),
        ),
        header_parameters={"AI-Resource-Group": RESOURCE_GROUP},
    )
    return {"result": result.to_dict()}
