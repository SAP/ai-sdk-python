"""
Embeddings Module Configuration Models
"""

from enum import Enum
from typing import Optional, Dict, List, Union

from pydantic import ConfigDict, Field

from gen_ai_hub.orchestration_v2.models.base import ABCBaseModel as BaseModel, ResponseBaseModel
from gen_ai_hub.orchestration_v2.models.data_masking import MaskingModuleConfig


class EmbeddingsEncodingFormat(str, Enum):
    """
    Encoding format for the embeddings output.

    Values:
        FLOAT: Returns embeddings as an array of floating point numbers.
        BASE64: Returns embeddings as a base64 encoded string.
        BINARY: Returns embeddings in binary format.
        INT8: Returns embeddings as an array of 8-bit integers.
        UINT8: Returns embeddings as an array of unsigned 8-bit integers.
        UBINARY: Returns embeddings in unsigned binary format.
    """
    FLOAT = "float"
    BASE64 = "base64"
    BINARY = "binary"
    INT8 = "int8"
    UINT8 = "uint8"
    UBINARY = "ubinary"


class EmbeddingsInputType(str, Enum):
    """
    Type hint for the embedding model about the purpose of the text.

    Some models use asymmetric embeddings for better search performance.

    Values:
        TEXT: General purpose text (default).
        DOCUMENT: Content to be searched/retrieved.
        QUERY: Short search queries.
        SEARCH_DOCUMENT: Content stored in a search index to be retrieved.
        SEARCH_QUERY: Query run against a search index.
        CLASSIFICATION: Text used in a classification task.
        CLUSTERING: Text used in a clustering task.
        IMAGE: Image input.
    """
    TEXT = "text"
    DOCUMENT = "document"
    QUERY = "query"
    SEARCH_DOCUMENT = "search_document"
    SEARCH_QUERY = "search_query"
    CLASSIFICATION = "classification"
    CLUSTERING = "clustering"
    IMAGE = "image"


class EmbeddingsModelParams(BaseModel):
    """
    Additional parameters for generating embeddings.

    Args:
        dimensions: The number of dimensions for the output embeddings.
        encoding_format: The format to return the embeddings in. Can be a single
            format or a list of formats (e.g. for Cohere models that support
            returning multiple encodings at once).
        normalize: Whether to normalize the embeddings.
    """
    dimensions: Optional[int] = None
    encoding_format: Optional[Union[EmbeddingsEncodingFormat, List[EmbeddingsEncodingFormat]]] = None
    normalize: Optional[bool] = None


class EmbeddingsModelDetails(BaseModel):
    """
    The model and parameters to be used for generating embeddings.

    Args:
        name: Name of the embedding model.
        version: Version of the model to be used. Defaults to "latest".
        params: Additional parameters for the model (dimensions, encoding_format, normalize).
        timeout: Timeout for the embeddings request in seconds. Ignored for Vertex AI models.
        max_retries: Maximum number of retries. Ignored for Vertex AI models.
    """
    name: str
    version: Optional[str] = "latest"
    params: Optional[EmbeddingsModelParams] = None
    timeout: Optional[int] = Field(default=600, ge=1, le=1200)
    max_retries: Optional[int] = Field(default=2, ge=0, le=5)


class EmbeddingsModelConfig(BaseModel):
    """
    Configuration for the embeddings model.

    Args:
        model: The embedding model details.
    """
    model: EmbeddingsModelDetails


class EmbeddingsModuleConfigs(BaseModel):
    """
    Module configurations for the embeddings endpoint.

    Args:
        embeddings: Required configuration for the embeddings model.
        masking: Optional configuration for data masking before embedding.
    """
    embeddings: EmbeddingsModelConfig
    masking: Optional[MaskingModuleConfig] = None


class EmbeddingsOrchestrationConfig(BaseModel):
    """
    Configuration for the Embeddings Orchestration endpoint.

    Args:
        modules: The module configurations including embeddings model and optional masking.
    """
    modules: EmbeddingsModuleConfigs


class EmbeddingsInput(BaseModel):
    """
    Input for the embeddings endpoint.

    Args:
        text: The text to embed. Can be a single string or a list of strings.
        type: Optional type hint for the embedding model (text, document, or query).
    """
    text: Union[str, List[str]]
    type_: Optional[EmbeddingsInputType] = Field(default=None, alias="type")


class EmbeddingMultiFormat(ResponseBaseModel):
    """
    A dictionary mapping encoding format names to their embeddings.

    Used when multiple encoding formats are requested at once (Cohere-specific).
    Each field holds the embedding in the corresponding encoding format and is
    only populated when that format was requested.

    Args:
        float_: Float encoding format - array of floating point numbers.
        int8: Int8 encoding format - array of 8-bit integers.
        uint8: Uint8 encoding format - array of unsigned 8-bit integers.
        base64_: Base64 encoding format - base64 encoded string.
        binary: Binary encoding format - array of integers.
        ubinary: Ubinary encoding format - array of unsigned integers.
    """
    float_: Optional[List[float]] = Field(default=None, alias="float")
    int8: Optional[List[int]] = None
    uint8: Optional[List[int]] = None
    base64_: Optional[str] = Field(default=None, alias="base64")
    binary: Optional[List[int]] = None
    ubinary: Optional[List[int]] = None

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
        frozen=False,
    )

    def model_dump(self, **kwargs):
        """Dumps the model using aliases and omitting unset formats."""
        kwargs.setdefault("by_alias", True)
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(**kwargs)


class EmbeddingsUsage(ResponseBaseModel):
    """
    Token usage information for the embeddings request.

    Args:
        prompt_tokens: The number of tokens used by the prompt.
        total_tokens: The total number of tokens used by the request.
    """
    prompt_tokens: int
    total_tokens: int


class EmbeddingResult(ResponseBaseModel):
    """
    A single embedding result.

    Args:
        object: The object type, always "embedding".
        embedding: The embedding vector (array of floats), a base64 string, or a
            mapping of encoding format names to embeddings when multiple formats
            were requested (Cohere-specific).
        index: The index of this embedding in the list.
    """
    object: str = "embedding"
    embedding: Union[List[float], str, EmbeddingMultiFormat]
    index: int


class EmbeddingsResponse(ResponseBaseModel):
    """
    The response from the embedding model, following OpenAI specification.

    Args:
        object: The object type, always "list".
        data: The list of embeddings generated by the model.
        model: The name of the model used to generate the embeddings.
        usage: Token usage information.
    """
    object: str = "list"
    data: List[EmbeddingResult]
    model: str
    usage: EmbeddingsUsage


class EmbeddingsPostResponse(ResponseBaseModel):
    """
    Response for an embeddings POST request.

    Args:
        request_id: Unique identifier for the request.
        intermediate_results: Optional results from intermediate modules (e.g., masking).
        final_result: The embeddings response from the model.
    """
    request_id: str
    intermediate_results: Optional[Dict] = None
    final_result: EmbeddingsResponse


class EmbeddingsRequest(BaseModel):
    """
    Request body for the embeddings endpoint.

    Args:
        config: The embeddings orchestration configuration.
        input: The input text to embed.
    """
    config: EmbeddingsOrchestrationConfig
    input: EmbeddingsInput

__all__ = ["EmbeddingsEncodingFormat", "EmbeddingsInputType", "EmbeddingsModelParams", "EmbeddingsModelDetails",
           "EmbeddingsModelConfig", "EmbeddingsModuleConfigs", "EmbeddingsOrchestrationConfig", "EmbeddingsInput",
           "EmbeddingMultiFormat", "EmbeddingsUsage", "EmbeddingResult", "EmbeddingsResponse",
           "EmbeddingsPostResponse", "EmbeddingsRequest"]
