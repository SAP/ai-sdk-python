from typing import Any

from fastapi import Body
from pydantic import BaseModel, Field

from gen_ai_hub.proxy.native.sap.client import RPTClient
from gen_ai_hub.proxy.native.sap.models import DataType, PredictionConfig, RPTRequest, TargetColumn

_DATE_COLS = {"ORDERDATE"}

_DEFAULT_CLASSIFICATION_ROWS = [
    {"PRODUCT": "Couch",        "PRICE": 999.99,  "ORDERDATE": "28-11-2025", "ID": "35",  "COSTCENTER": "[PREDICT]"},
    {"PRODUCT": "Office Chair", "PRICE": 150.80,  "ORDERDATE": "02-11-2025", "ID": "44",  "COSTCENTER": "Office Furniture"},
    {"PRODUCT": "Server Rack",  "PRICE": 2200.00, "ORDERDATE": "01-11-2025", "ID": "104", "COSTCENTER": "Data Infrastructure"},
]

_DEFAULT_CLASSIFICATION_COLUMNS = {
    "PRODUCT":    ["Couch", "Office Chair", "Server Rack"],
    "PRICE":      [999.99, 150.8, 2200.00],
    "ORDERDATE":  ["28-11-2025", "02-11-2025", "01-11-2025"],
    "ID":         ["35", "44", "104"],
    "COSTCENTER": ["[PREDICT]", "Office Furniture", "Data Infrastructure"],
}

_DEFAULT_REGRESSION_ROWS = [
    {"PRODUCT": "Couch",           "PRICE": 999.99,  "ORDERDATE": "28-11-2025", "ID": "35",  "DISCOUNT_RATE": "[PREDICT]"},
    {"PRODUCT": "Office Chair",    "PRICE": 150.80,  "ORDERDATE": "02-11-2025", "ID": "44",  "DISCOUNT_RATE": 0.12},
    {"PRODUCT": "Server Rack",     "PRICE": 2200.00, "ORDERDATE": "01-11-2025", "ID": "104", "DISCOUNT_RATE": 0.05},
    {"PRODUCT": "Standing Desk",   "PRICE": 640.00,  "ORDERDATE": "05-11-2025", "ID": "205", "DISCOUNT_RATE": 0.10},
    {"PRODUCT": "Monitor 27 inch", "PRICE": 289.99,  "ORDERDATE": "08-11-2025", "ID": "306", "DISCOUNT_RATE": "[PREDICT]"},
]


def _infer_schema(rows: list[dict[str, Any]]) -> dict[str, DataType]:
    """Derive column DataTypes from the first fully-populated (non-predict) row."""
    for row in rows:
        if "[PREDICT]" not in row.values():
            return {
                k: DataType(dtype="date" if k in _DATE_COLS else ("numeric" if isinstance(v, (int, float)) else "string"))
                for k, v in row.items()
            }
    return {}


class PredictByRowsRequest(BaseModel):
    rows: list[dict[str, Any]] = Field(
        default=_DEFAULT_CLASSIFICATION_ROWS,
        description="Row-oriented data. Mark cells to predict with the prediction_placeholder value.",
    )
    target_column: str = Field(default="COSTCENTER", description="Column to predict.")
    task_type: str = Field(default="classification", description="'classification' or 'regression'.")
    prediction_placeholder: str = Field(default="[PREDICT]", description="Sentinel value marking cells to predict.")
    index_column: str = Field(default="ID", description="Row identifier column.")
    model_name: str = Field(default="sap-rpt-1-small", description="SAP RPT model to use.")


class PredictByColumnsRequest(BaseModel):
    columns: dict[str, list[Any]] = Field(
        default=_DEFAULT_CLASSIFICATION_COLUMNS,
        description="Column-oriented data. Each key is a column name, value is the list of cells.",
    )
    target_column: str = Field(default="COSTCENTER")
    task_type: str = Field(default="classification")
    prediction_placeholder: str = Field(default="[PREDICT]")
    model_name: str = Field(default="sap-rpt-1-small")


class RegressionRequest(BaseModel):
    rows: list[dict[str, Any]] = Field(
        default=_DEFAULT_REGRESSION_ROWS,
        description="Row-oriented data with a numeric target column.",
    )
    target_column: str = Field(default="DISCOUNT_RATE")
    prediction_placeholder: str = Field(default="[PREDICT]")
    index_column: str = Field(default="ID")
    model_name: str = Field(default="sap-rpt-1-small")


def predict_by_rows(body: PredictByRowsRequest = Body(default=None)):
    """
    Classify or regress a target column using row-oriented input.

    Omit the request body to use the built-in sample data.
    Provide your own rows to run predictions on custom data.
    """
    if body is None:
        body = PredictByRowsRequest()
    rpt_body = RPTRequest(
        prediction_config=PredictionConfig(
            target_columns=[TargetColumn(
                name=body.target_column,
                prediction_placeholder=body.prediction_placeholder,
                task_type=body.task_type,
            )]
        ),
        index_column=body.index_column,
        rows=body.rows,
        data_schema=_infer_schema(body.rows),
    )
    return RPTClient().predict(body=rpt_body, model_name=body.model_name)


def predict_by_columns(body: PredictByColumnsRequest = Body(default=None)):
    """
    Classify a target column using column-oriented input.

    Omit the request body to use the built-in sample data.
    """
    if body is None:
        body = PredictByColumnsRequest()
    n = max(len(v) for v in body.columns.values())
    rows = [{k: body.columns[k][i] for k in body.columns} for i in range(n)]
    rpt_body = RPTRequest(
        prediction_config=PredictionConfig(
            target_columns=[TargetColumn(
                name=body.target_column,
                prediction_placeholder=body.prediction_placeholder,
                task_type=body.task_type,
            )]
        ),
        columns=body.columns,
        data_schema=_infer_schema(rows),
    )
    return RPTClient().predict(body=rpt_body, model_name=body.model_name)


def regression(body: RegressionRequest = Body(default=None)):
    """
    Predict a numeric target column (regression).

    Omit the request body to use the built-in sample data.
    """
    if body is None:
        body = RegressionRequest()
    rpt_body = RPTRequest(
        prediction_config=PredictionConfig(
            target_columns=[TargetColumn(name=body.target_column, task_type="regression")]
        ),
        index_column=body.index_column,
        rows=body.rows,
        data_schema=_infer_schema(body.rows),
    )
    return RPTClient().predict(body=rpt_body, model_name=body.model_name)
