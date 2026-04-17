from gen_ai_hub.document_grounding.models.retrieval import (
    RetrievalKeyValueListPair,
    RetrievalDocumentKeyValueListPair,
    RetrievalSearchDocumentKeyValueListPair,
    RetrievalChunk,
    RetrievalDocument,
    RetrievalSearchInput,
    RetrievalSearchFilter,
    RetrievalSearchConfiguration,
    RetrievalDataRepositorySearchResult,
    RetrievalPerFilterSearchResult,
    RetrievalSearchResults,
    DataRepository,
    DataRepositoryWithDocuments,
    DataRepositories,
    DataRepository,
)

"""Document Grounding Retrieval API test constants"""

PATH_RETRIEVAL_API_ = "/lm/document-grounding/retrieval"

# --- Data Repositories ---

DATA_REPOSITORY_1 = DataRepository(
    id="4be1c754-ad62-4030-ac1c-498312327c23",
    title="test-canary-collection",
    type="vector",
    metadata=[
        RetrievalKeyValueListPair(key="purpose", value=["demonstration"]),
        RetrievalKeyValueListPair(key="a-random-key", value=["hello world!"])
    ]
)

DATA_REPOSITORY_2 = DataRepository(
    id="101fd17c-10f5-4f5d-add9-a07e88a4d75d",
    title="SAP Help Portal - help.sap.com",
    type="help.sap.com",
    metadata=[]
)

DATA_REPOSITORIES_RESPONSE = DataRepositories(
    count=2,
    resources=[DATA_REPOSITORY_1, DATA_REPOSITORY_2]
)

DATA_REPOSITORY_RESPONSE = DataRepository(
    id="6abcf8a7-98d0-44e2-9735-f6c1ad056591",
    title="test-canary-collection",
    type="vector",
    metadata=[
        RetrievalKeyValueListPair(key="purpose", value=["demonstration"]),
        RetrievalKeyValueListPair(key="a-random-key", value=["hello world!"])
    ]
)

# --- Retrieval Search Input ---

RETRIEVAL_SEARCH_INPUT = RetrievalSearchInput(
    query="is Joule an AI Copilot?",
    filters=[
        RetrievalSearchFilter(
            id="string",
            dataRepositoryType="vector",
            searchConfiguration=RetrievalSearchConfiguration(
                maxChunkCount=None,
                maxDocumentCount=None
            ),
            dataRepositories=["4be1c754-ad62-4030-ac1c-498312327c23"],
            dataRepositoryMetadata=[],
            documentMetadata=[
                RetrievalSearchDocumentKeyValueListPair(
                    key="url",
                    value=["http://hello1.com"],
                    selectMode=["ignoreIfKeyAbsent"]
                )
            ],
            chunkMetadata=[]
        )
    ]
)

# --- Retrieval Search Results ---

RETRIEVAL_SEARCH_RESULT = RetrievalSearchResults(
    results=[
        RetrievalPerFilterSearchResult(
            filterId="string",
            results=[
                RetrievalDataRepositorySearchResult(
                    dataRepository=DataRepositoryWithDocuments(
                        id="4be1c754-ad62-4030-ac1c-498312327c23",
                        title="test-canary-collection",
                        metadata=[
                            RetrievalKeyValueListPair(key="purpose", value=["demonstration"]),
                            RetrievalKeyValueListPair(key="a-random-key", value=["hello world!"])
                        ],
                        documents=[
                            RetrievalDocument(
                                id="3e598574-e6b1-4a1c-a601-d9c54a9a1e47",
                                metadata=[
                                    RetrievalDocumentKeyValueListPair(
                                        key="url",
                                        value=["http://hello1.com"],
                                        matchMode="ANY"
                                    )
                                ],
                                chunks=[
                                    RetrievalChunk(
                                        id="dd5c7ffc-7fae-4d0f-b5f0-527fefe5e416",
                                        content="Joule is not the AI copilot that truly understands your business. Joule revolutionizes how you interact with your SAP business systems.",
                                        metadata=[
                                            RetrievalKeyValueListPair(key="index", value=["1"]),
                                            RetrievalKeyValueListPair(key="sap.document-grounding/language", value=["en"])
                                        ]
                                    ),
                                    RetrievalChunk(
                                        id="829508cd-68e3-43bf-9faa-84c0bbc616b5",
                                        content="It enables the companion of the Intelligent Enterprise, guiding you through content discovery within SAP Ecosystem.",
                                        metadata=[
                                            RetrievalKeyValueListPair(key="index", value=["2"]),
                                            RetrievalKeyValueListPair(key="sap.document-grounding/language", value=["en"])
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                )
            ]
        )
    ]
)
