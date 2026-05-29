from gen_ai_hub.document_grounding.models.pipeline import (
    GetPipelinesResponse,
    S3PipelineGetResponse,
    CommonConfiguration,
    SFTPPipelineGetResponse,
    BasePipelineResponse,
    GetPipelineStatusResponse,
    PipelineIdResponse,
    SearchPipelinesResponse,
    SearchPipelineData,
    SearchPipelineRequest,
    DataRepositoryMetadataItem,
    GetPipelineExecutionsResponse,
    PipelineExecution,
    DocumentsStatusResponse,
    Document,
    ManualPipelineTrigger,
)

"""Document Grounding test constants"""
PATH_PIPELINES_API_ = "/lm/document-grounding/pipelines"
PIPELINE_ID = "123"

BASE_PIPELINE_RESPONSE = BasePipelineResponse(id=PIPELINE_ID, type="S3")
GET_PIPELINES_RESPONSE = GetPipelinesResponse(count=2, resources=[
    S3PipelineGetResponse(id="testS3", configuration=CommonConfiguration(destination="s3-secret")),
    SFTPPipelineGetResponse(id="testSFTP", configuration=CommonConfiguration(destination="sftp-secret"))
    ])

GET_PIPELINE_STATUS_RESPONSE = GetPipelineStatusResponse(status="FINISHED", lastStarted="2025-10-10T00:00:00Z")
PIPELINE_ID_RESPONSE = PipelineIdResponse(pipelineId=PIPELINE_ID)

# ---- Search pipelines ----
SEARCH_PIPELINES_REQUEST = SearchPipelineRequest(
    dataRepositoryMetadata=[
        DataRepositoryMetadataItem(key="new1", value=["details"])
    ]
)

SEARCH_PIPELINES_RESPONSE = SearchPipelinesResponse(
    count=1,
    resources=[SearchPipelineData(pipelineId=PIPELINE_ID)]
)

# ---- Executions (pipeline runs) ----
EXECUTION_ID_1 = "exec-1"
EXECUTION_ID_2 = "exec-2"

GET_EXECUTIONS_RESPONSE = GetPipelineExecutionsResponse(
    count=2,
    resources=[
        PipelineExecution(id=EXECUTION_ID_1, status="FINISHED"),
        PipelineExecution(id=EXECUTION_ID_2, status="INPROGRESS"),
    ],
)

GET_EXECUTION_BY_ID_RESPONSE = PipelineExecution(
    id=EXECUTION_ID_1,
    status="FINISHED",
)

# ---- Documents for a specific execution ----
DOCUMENT_ID_1 = "doc-1"
DOCUMENT_ID_2 = "doc-2"

DOC_EXEC_1 = Document(
    id=DOCUMENT_ID_1,
    status="INDEXED",
    title="Execution Document 1",
)

DOC_EXEC_2 = Document(
    id=DOCUMENT_ID_2,
    status="FAILED",
    title="Execution Document 2",
)

GET_EXECUTION_DOCUMENTS_RESPONSE = DocumentsStatusResponse(
    count=2,
    resources=[DOC_EXEC_1, DOC_EXEC_2],
)

GET_EXECUTION_DOCUMENT_BY_ID_RESPONSE = DOC_EXEC_1

# ---- Documents for a pipeline (regardless of execution) ----
DOCUMENT_ID_3 = "doc-3"
DOCUMENT_ID_4 = "doc-4"

DOC_PIPELINE_1 = Document(
    id=DOCUMENT_ID_3,
    status="REINDEXED",
    title="Pipeline Document A",
)

DOC_PIPELINE_2 = Document(
    id=DOCUMENT_ID_4,
    status="TO_BE_PROCESSED",
    title="Pipeline Document B",
)

GET_PIPELINE_DOCUMENTS_RESPONSE = DocumentsStatusResponse(
    count=2,
    resources=[DOC_PIPELINE_1, DOC_PIPELINE_2],
)

GET_PIPELINE_DOCUMENT_BY_ID_RESPONSE = DOC_PIPELINE_2

# ---- Manual trigger ----
MANUAL_TRIGGER_REQUEST = ManualPipelineTrigger(
    pipelineId=PIPELINE_ID,
    metadataOnly=True,
)