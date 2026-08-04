"""Readable type aliases for the RPT 1.5 request/response models.

The OpenAPI spec defines ``PredictRequestPayload`` as a ``oneOf`` of two
concrete schemas that differ only in how the input data is provided.  The
generator names them ``PredictRequestPayloadOneOf`` / ``PredictRequestPayloadOneOf1``
which gives users no hint about when to use which.  This module re-exports
them under descriptive names alongside all other public model types.
"""

from collections.abc import Mapping, Sequence
from typing import Any

from generated.models.predict_request_payload_one_of import (
    PredictRequestPayloadOneOf as RowsRequest,
)
from generated.models.predict_request_payload_one_of1 import (
    PredictRequestPayloadOneOf1 as ColumnsRequest,
)
from generated.models.predict_response_metadata import PredictResponseMetadata
from generated.models.predict_response_payload import PredictResponsePayload
from generated.models.predict_response_status import PredictResponseStatus
from generated.models.prediction_config import PredictionConfig
from generated.models.prediction_placeholder import PredictionPlaceholder
from generated.models.prediction_result import PredictionResult
from generated.models.rows_inner_value import RowsInnerValue
from generated.models.schema_field_config import SchemaFieldConfig
from generated.models.target_column_config import TargetColumnConfig

CellValue = str | float | int | None


def rows_request(
    prediction_config: PredictionConfig,
    rows: Sequence[Mapping[str, Any]],
    index_column: str | None = None,
    parse_data_types: bool | None = True,
) -> RowsRequest:
    """Build a :class:`RowsRequest` from plain dicts.

    Each row is a ``dict[column_name, value]`` with primitive values.
    Define a ``TypedDict`` for your row shape to get key autocomplete::

        class SalesRow(TypedDict):
            PRODUCT: str
            PRICE: float
            SALESGROUP: str

        rows_request(prediction_config=..., rows=[SalesRow(...)])
    """
    return RowsRequest(
        prediction_config=prediction_config,
        index_column=index_column,
        parse_data_types=parse_data_types,
        rows=[
            {k: RowsInnerValue(v) for k, v in row.items()}
            for row in rows
        ],
    )


def columns_request(
    prediction_config: PredictionConfig,
    columns: dict[str, list[CellValue]],
    index_column: str | None = None,
    parse_data_types: bool | None = True,
) -> ColumnsRequest:
    """Build a :class:`ColumnsRequest` from plain column lists.

    ``columns`` maps each column name to its list of values::

        columns_request(
            prediction_config=...,
            columns={
                "PRODUCT": ["Laptop", "Chair"],
                "PRICE":   [999.99, 142.99],
            },
        )
    """
    return ColumnsRequest(
        prediction_config=prediction_config,
        index_column=index_column,
        parse_data_types=parse_data_types,
        columns={
            col: [RowsInnerValue(v) for v in vals]
            for col, vals in columns.items()
        },
    )


__all__ = [
    "CellValue",
    "ColumnsRequest",
    "PredictResponseMetadata",
    "PredictResponsePayload",
    "PredictResponseStatus",
    "PredictionConfig",
    "PredictionPlaceholder",
    "PredictionResult",
    "RowsInnerValue",
    "RowsRequest",
    "SchemaFieldConfig",
    "TargetColumnConfig",
    "columns_request",
    "rows_request",
]
