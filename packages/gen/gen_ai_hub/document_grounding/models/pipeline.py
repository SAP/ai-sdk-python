"""Pydantic models for Pipeline API.

This module defines data models for the Pipeline API, which manages document
vectorization pipelines from various data sources (Microsoft SharePoint, AWS S3, SFTP).

Model categories:
    - Pipeline configuration models (create/get requests and responses)
    - Pipeline execution models (tracking pipeline runs)
    - Document models (tracking document processing status)
    - Search and metadata models (filtering pipelines by metadata)
    - Trigger models (manual pipeline execution)

All models use Pydantic for validation and serialization.
"""
from typing import List, Optional, Union, Annotated, Literal
from pydantic import Field
from datetime import datetime
from enum import Enum

from gen_ai_hub._base_model import SdkBaseModel

# --- Models for Pipeline API ---

class MetaData(SdkBaseModel):
    destination: str

class SharePointSite(SdkBaseModel):
    name: str
    includePaths: Optional[List[str]] = None

class SharePointConfig(SdkBaseModel):
    site: SharePointSite

class MSSharePointConfiguration(SdkBaseModel):
    destination: str
    sharePoint: SharePointConfig

class CommonConfiguration(SdkBaseModel):
    destination: str

class MSSharePointPipelineCreateRequest(SdkBaseModel):
    type: Literal["MSSharePoint"] = "MSSharePoint"
    configuration: MSSharePointConfiguration
    metadata: Optional[MetaData] = None

class S3PipelineCreateRequest(SdkBaseModel):
    type: Literal["S3"] = "S3"
    configuration: CommonConfiguration
    metadata: Optional[MetaData] = None

class SFTPPipelineCreateRequest(SdkBaseModel):
    type: Literal["SFTP"] = "SFTP"
    configuration: CommonConfiguration
    metadata: Optional[MetaData] = None

CreatePipelineRequest = Union[
    MSSharePointPipelineCreateRequest,
    S3PipelineCreateRequest,
    SFTPPipelineCreateRequest
]

class PipelineIdResponse(SdkBaseModel):
    pipelineId: str

class BasePipelineResponse(SdkBaseModel):
    id: str
    type: str
    metadata: Optional[MetaData] = None

class MSSharePointConfigurationGetResponse(SdkBaseModel):
    destination: str
    sharePoint: SharePointConfig

class MSSharePointPipelineGetResponse(BasePipelineResponse):
    type: Literal["MSSharePoint"] = "MSSharePoint"
    configuration: MSSharePointConfigurationGetResponse

class S3PipelineGetResponse(BasePipelineResponse):
    type: Literal["S3"] = "S3"
    configuration: CommonConfiguration

class SFTPPipelineGetResponse(BasePipelineResponse):
    type: Literal["SFTP"] = "SFTP"
    configuration: CommonConfiguration

GetPipelineResponse = Annotated[
    MSSharePointPipelineGetResponse | S3PipelineGetResponse | SFTPPipelineGetResponse,
    Field(discriminator="type")
]

class GetPipelinesResponse(SdkBaseModel):
    count: Optional[int]
    resources: List[GetPipelineResponse]

class GetPipelineStatusResponse(SdkBaseModel):
    lastStarted: Optional[str]
    status: Optional[str]

# --- Search ---

class DataRepositoryMetadataItem(SdkBaseModel):
    key: str
    value: List[str]


class SearchPipelineRequest(SdkBaseModel):
    dataRepositoryMetadata: List[DataRepositoryMetadataItem]


class SearchPipelineData(SdkBaseModel):
    pipelineId: str


class SearchPipelinesResponse(SdkBaseModel):
    count: Optional[int]
    resources: List[SearchPipelineData]


# --- Executions (Pipeline Runs) ---

class PipelineExecutionStatus(str, Enum):
    NEW = "NEW"
    UNKNOWN = "UNKNOWN"
    INPROGRESS = "INPROGRESS"
    FINISHED = "FINISHED"
    FINISHED_WITH_ERRORS = "FINISHEDWITHERRORS"
    TIMEOUT = "TIMEOUT"

class PipelineExecution(SdkBaseModel):
    id: str
    status: Optional[PipelineExecutionStatus] = None
    createdAt: Optional[datetime] = None
    modifiedAt: Optional[datetime] = None


class GetPipelineExecutionsResponse(SdkBaseModel):
    count: Optional[int]
    resources: List[PipelineExecution]


# --- Documents ---

class DocumentStatus(str, Enum):
    TO_BE_PROCESSED = "TO_BE_PROCESSED"
    INDEXED = "INDEXED"
    REINDEXED = "REINDEXED"
    DEINDEXED = "DEINDEXED"
    FAILED = "FAILED"
    FAILED_TO_BE_RETRIED = "FAILED_TO_BE_RETRIED"
    TO_BE_SCHEDULED = "TO_BE_SCHEDULED"

class Document(SdkBaseModel):
    id: str
    status: Optional[DocumentStatus] = None
    viewLocation: Optional[str] = None
    downloadLocation: Optional[str] = None
    absoluteUrl: Optional[str] = None
    title: Optional[str] = None
    metadataId: Optional[str] = None
    createdTimestamp: Optional[datetime] = None
    lastUpdatedTimestamp: Optional[datetime] = None


class DocumentsStatusResponse(SdkBaseModel):
    count: Optional[int]
    resources: List[Document]


# --- Trigger ---

class ManualPipelineTrigger(SdkBaseModel):
    pipelineId: str
    metadataOnly: Optional[bool] = None
