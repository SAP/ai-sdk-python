from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client
from gen_ai_hub.document_grounding_generation import (
    GroundingApiClient,
    DataRepositoryType,
    FiltersInner,
    RetrievalApi,
    RetrievalSearchConfiguration,
    RetrievalSearchFilter,
    RetrievalSearchInput,
)


async def retrieval_search():
    client = GroundingApiClient(get_proxy_client())
    result = await RetrievalApi(client).search(
        ai_resource_group="default",
        retrieval_search_input=RetrievalSearchInput(
            query="Features of Generative AI Hub",
            filters=[
                FiltersInner(
                    RetrievalSearchFilter(
                        id="SAPHelp",
                        data_repository_type=DataRepositoryType.HELP_DOT_SAP_DOT_COM,
                        search_configuration=RetrievalSearchConfiguration(
                            max_chunk_count=5
                        ),
                    )
                )
            ],
        ),
    )
    return {"result": result.to_dict()}
