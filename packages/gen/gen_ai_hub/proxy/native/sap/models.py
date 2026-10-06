from typing import Annotated, Optional, Literal, Union, Any
from pydantic import BaseModel, Field, RootModel, model_validator


class TargetColumn(BaseModel):
    """Represents a target column in data.

    :param name: Name of the target column.
    :type name: str
    :param prediction_placeholder: The prediction placeholder in any column for which to predict a value. The model will predict a value for all table cells containing this value.
    :type prediction_placeholder: Optional[Union[str, int, float]]
    :param task_type: Task type of the target column.
        One of ``"classification"`` or ``"regression"``. Defaults to ``None``.
    :type task_type: Optional[Literal["classification", "regression"]]
    :param top_k: How many predictions to output for this classification column.If not provided, only a single prediction is returned. Only relevant for classification.
    :type top_k: Optional[int]
    """

    name: str
    prediction_placeholder: Optional[Union[str, int, float]]
    task_type: Optional[Literal["classification", "regression"]] = None
    top_k: Optional[int] = None


class ExplanationConfig(BaseModel):
    """
    Configuration for explainability outputs.

    :param top_column_scores: For how many columns to output column scores (optional, default is 0). 0 by default (no explainability). Max value is 20.
    :type top_column_scores: int
    :param top_relevant_context_rows: For how many context rows to return indices per query row (optional, default is 0). 0 by default (no explainability). Max value is 20.
    :type top_relevant_context_rows: int
    """

    top_column_scores: int = Field(default=0, ge=0, le=20)
    top_relevant_context_rows: int = Field(default=0, ge=0, le=20)


class ExplanationResult(BaseModel):
    """
    Explanation data for predictions.

    :param top_column_scores: Column scores per query row extracted from the model (higher means more weight was put on this column).
    :type top_column_scores: Optional[list[dict[str, Union[int, float]]]]
    :param top_relevant_context_rows: 2D array where each subarray contains indices of most relevant context rows for that query row. The first dimension indexes query rows, the second dimension indexes all rows as a sequential integer index.
    :type top_relevant_context_rows: Optional[list[list[int]]]
    """

    top_column_scores: Optional[list[dict[str, Union[int, float]]]]
    top_relevant_context_rows: Optional[list[list[int]]]


class PredictionConfig(BaseModel):
    """
    The configuration object specifying which columns to predict

    :param target_columns: List of target columns to predict.
    :type target_columns: list[TargetColumn]
    :param explanations: Optional configuration for explainability outputs (column scores and relevant context rows).
    :type explanations: Optional[ExplanationConfig]
    :param context_mode: Context mode for predictions. Set it to \"default\" for the best balance between accuracy and latency/cost. Set it to \"deep\" for higher accuracy with >8k context rows at increased latency and cost (only for \"sap-rpt-1.6-large\").
    :type context_mode: Literal['default', 'deep']
    """

    target_columns: list[TargetColumn]
    explanations: Optional[ExplanationConfig] = None
    context_mode: Literal['default', 'deep'] = 'default'


class DataType(BaseModel):
    """Schema definition for a column.

    :param dtype: The data type of the column.
    :type dtype: Literal['string', 'numeric', 'date',
        'time', 'boolean', 'largestring', 'uuid', 'integer', 'int16',
        'int32', 'int64', 'uint8', 'decimal',
        'double', 'datetime', 'timestamp']
    """

    dtype: Literal['string', 'numeric', 'date',
                   'time', 'boolean', 'largestring',
                   'uuid', 'integer', 'int16',
                   'int32', 'int64', 'uint8', 'decimal',
                   'double', 'datetime', 'timestamp']


class RPTRequest(BaseModel):
    """Request model for predictions.

    Provide exactly one of ``rows`` or ``columns``.

    :param prediction_config: Configuration describing what to predict.
    :type prediction_config: PredictionConfig
    :param index_column: Name of a column used to identify the row. This column is not used
        as an input feature and may be returned in the response objects.
    :type index_column: Optional[str]
    :param rows: Array of objects representing table rows (both context and query rows).
    :type rows: Optional[list[dict]]
    :param columns: Mapping from column name to array of column values.
    :type columns: Optional[dict[str, list]]
    :param data_schema: Schema definition for all columns, e.g.
        ``{"columnA": {"dtype": "string"}, "columnB": {"dtype": "numeric"}}``.
    :type data_schema: Optional[dict[str, DataType]]
    :param parse_data_types: Relevant when ``data_schema`` is not provided. Whether to parse data types
        (e.g., interpret strings as numbers or dates). Defaults to ``True``.
    :type parse_data_types: bool
    """

    prediction_config: PredictionConfig
    index_column: Optional[str] = None
    rows: Optional[list[dict]] = None
    columns: Optional[dict[str, list]] = None
    data_schema: Optional[dict[str, DataType]] = None
    parse_data_types: bool = True

    @model_validator(mode="after")
    def validate_rows_xor_columns(self):
        """Validate that exactly one of ``rows`` or ``columns`` is provided.

        :raises ValueError: If neither or both of ``rows`` and ``columns`` are provided.
        :return: The validated request instance.
        :rtype: RPTRequest
        """
        if (self.rows is None) == (self.columns is None):
            raise ValueError("Exactly one of 'rows' or 'columns' must be provided.")
        return self

    def model_dump(self, **kwargs):
        """Serialize the model to a dictionary.

        Ensures the non-provided alternative (``rows`` or ``columns``) is omitted from the dump
        and that ``None`` values are excluded.

        :param kwargs: Keyword arguments forwarded to ``pydantic.BaseModel.model_dump``.
        :type kwargs: Any
        :return: Serialized dictionary representation of the model.
        :rtype: dict
        """
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(**kwargs)


class ResponseMetadata(BaseModel):
    """Response metadata.

    :param num_rows: Total number of input rows.
    :type num_rows: int
    :param num_columns: Total number of input columns.
    :type num_columns: int
    :param num_predictions: Number of table cells containing the specified placeholder values,
        summed over all target columns.
    :type num_predictions: int
    :param num_query_rows: Number of query rows for which a prediction was made.
    :type num_query_rows: int
    :param context_mode: The context mode used for this prediction request.
    :type context_mode: Literal['default', 'deep']
    """

    num_rows: int
    num_columns: int
    num_predictions: int
    num_query_rows: int
    context_mode: Literal['default', 'deep'] = 'default'


class ResponseStatus(BaseModel):
    """Status information for a prediction request.

    :param code: Numeric status code.
    :type code: int
    :param message: Status message.
    :type message: str
    """

    code: int
    message: str


class PredictionItem(BaseModel):
    """Single prediction result.

    :param prediction: The predicted value.
    :type prediction: Union[str, float]
    :param confidence: Confidence score for classification tasks, in the range ``[0.0, 1.0]``. Defaults to ``None``.
    :type confidence: Optional[float]
    :param confidence_interval: Lower and upper bounds of the confidence interval. Null for classification predictions.
    :type confidence_interval: Optional[tuple[float, float]]
    """

    prediction: Union[str, float]
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    confidence_interval: Optional[Annotated[list[float], Field(min_length=2, max_length=2)]] = None


class Prediction(RootModel[dict[str, Union[list[PredictionItem], Any]]]):
    """Container for prediction results keyed by target column name."""

    def __getitem__(self, key):
        """Return the prediction payload for ``key``.

        :param key: Prediction key to access.
        :type key: str
        :return: Value associated with ``key``.
        :rtype: Any
        """
        return self.root[key]


class RPTResponse(BaseModel):
    """Response model for an RPT request.

    :param id: Unique identifier for the response.
    :type id: str
    :param status: Status describing the outcome of the request.
    :type status: ResponseStatus
    :param predictions: Prediction data returned by the service.
    :type predictions: list[Prediction]
    :param explanations: Explanation data containing context row and column scores.
    :type explanations: Optional[ExplanationResult]
    :param metadata: Metadata about the request/response.
    :type metadata: ResponseMetadata
    """

    id: str
    status: ResponseStatus
    predictions: list[Prediction]
    explanations: Optional[ExplanationResult] = None
    metadata: ResponseMetadata


class ErrorResponseDetails(BaseModel):
    """Details of an error response.

    :param loc: Location in the request where the error occurred.
    :type loc: list
    :param msg: Human-readable error message.
    :type msg: str
    :param type: Error category/type.
    :type type: str
    """

    loc: list
    msg: str
    type: str


class RPTException(Exception):
    """Exception representing an error response from the RPT service.

    :param status: Status indicating the error category/type.
    :type status: ResponseStatus
    :param detail: Optional list of additional error details.
    :type detail: Optional[list[ErrorResponseDetails]]
    """
    def __init__(self,
                 status: ResponseStatus,
                 detail: Optional[list[ErrorResponseDetails]] = None
                 ):
        self.status = status
        self.detail = detail
