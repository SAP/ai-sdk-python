expected = { # Pipeline models
    "CreatePipelineRequest",
    "MSSharePointPipelineCreateRequest",
    "S3PipelineCreateRequest",
    "SFTPPipelineCreateRequest",
    "SearchPipelineRequest",
    "DataRepositoryMetadataItem",
    "CommonConfiguration",
    "MetaData",
    "MSSharePointConfiguration",
    "SharePointConfig",
    "SharePointSite",
    "ManualPipelineTrigger",
    "PipelineIdResponse",
    "GetPipelineResponse",
    "GetPipelinesResponse",
    "GetPipelineStatusResponse",
    "PipelineExecution",
    "GetPipelineExecutionsResponse",
    "Document",
    "DocumentsStatusResponse",
    "MSSharePointPipelineGetResponse",
    "S3PipelineGetResponse",
    "SFTPPipelineGetResponse",
    "SearchPipelineData",
    "SearchPipelinesResponse",
    "PipelineExecutionStatus",
    "DocumentStatus",
    "BasePipelineResponse",
    "MSSharePointConfigurationGetResponse",
    # Retrieval models
    "RetrievalKeyValueListPair",
    "RetrievalDocumentKeyValueListPair",
    "RetrievalSearchDocumentKeyValueListPair",
    "RetrievalChunk",
    "RetrievalDocument",
    "DataRepositoryType",
    "DataRepository",
    "DataRepositoryWithDocuments",
    "RetrievalSearchConfiguration",
    "RetrievalSearchFilter",
    "RetrievalSearchInput",
    "RetrievalDataRepositorySearchResult",
    "RetrievalPerFilterSearchResult",
    "RetrievalPerFilterSearchResultError",
    "RetrievalPerFilterSearchResultWithError",
    "RetrievalSearchResults",
    "DataRepositories",
    # Vector models
    "VectorKeyValueListPair",
    "EmbeddingConfig",
    "CollectionCreateRequest",
    "Collection",
    "CollectionsListResponse",
    "TextOnlyBaseChunk",
    "BaseDocument",
    "DocumentWithoutChunks",
    "VectorDocument",
    "DocumentsCreateRequest",
    "DocumentsUpdateRequest",
    "DocumentsListResponse",
    "DocumentsResponse",
    "CollectionCreatedResponse",
    "CollectionDeletedResponse",
    "CollectionPendingResponse",
    "CollectionCreationStatusResponse",
    "CollectionDeletionStatusResponse",
    "VectorSearchConfiguration",
    "VectorSearchDocumentKeyValueListPair",
    "VectorSearchFilter",
    "TextSearchRequest",
    "VectorChunk",
    "DocumentOutput",
    "DocumentsChunk",
    "VectorPerFilterSearchResult",
    "VectorSearchResults",
    # Clients
    "PipelineAPIClient",
    "RetrievalAPIClient",
    "VectorAPIClient"
}

def test_flat_import_document_grounding_all():
    import gen_ai_hub.document_grounding as module
    assert set(module.__all__) == expected

def test_flat_import_document_grounding_by_name():
    from gen_ai_hub.document_grounding import PipelineAPIClient as client_flat
    from gen_ai_hub.document_grounding.client import PipelineAPIClient as client
    assert client_flat == client

    from gen_ai_hub.document_grounding import VectorAPIClient as vector_client_flat
    from gen_ai_hub.document_grounding.client import VectorAPIClient as vector_client
    assert vector_client_flat == vector_client

    from gen_ai_hub.document_grounding import RetrievalAPIClient as retrieval_client_flat
    from gen_ai_hub.document_grounding.client import RetrievalAPIClient as retrieval_client
    assert retrieval_client_flat == retrieval_client

    from gen_ai_hub.document_grounding import CreatePipelineRequest as create_pipeline_request_flat
    from gen_ai_hub.document_grounding.models.pipeline import CreatePipelineRequest as create_pipeline_request
    assert create_pipeline_request_flat == create_pipeline_request

    from gen_ai_hub.document_grounding import RetrievalSearchConfiguration as retrieval_search_configuration_flat
    from gen_ai_hub.document_grounding.models.retrieval import RetrievalSearchConfiguration as retrieval_search_configuration
    assert retrieval_search_configuration_flat == retrieval_search_configuration

    from gen_ai_hub.document_grounding import DocumentsCreateRequest as documents_create_request_flat
    from gen_ai_hub.document_grounding.models.vector import DocumentsCreateRequest as documents_create_request
    assert documents_create_request_flat == documents_create_request
