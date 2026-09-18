from gen_ai_hub.proxy.native.sap.client import RPTClient
from gen_ai_hub.proxy.native.sap.models import DataType, PredictionConfig, RPTRequest, TargetColumn

MODEL_NAME = "sap-rpt-1-small"

CLASSIFICATION_SCHEMA = {
    "PRODUCT": DataType(dtype="string"),
    "PRICE": DataType(dtype="numeric"),
    "ORDERDATE": DataType(dtype="date"),
    "ID": DataType(dtype="string"),
    "COSTCENTER": DataType(dtype="string"),
}

CLASSIFICATION_ROWS = [
    {"PRODUCT": "Couch", "PRICE": 999.99, "ORDERDATE": "28-11-2025", "ID": "35", "COSTCENTER": "[PREDICT]"},
    {"PRODUCT": "Office Chair", "PRICE": 150.8, "ORDERDATE": "02-11-2025", "ID": "44", "COSTCENTER": "Office Furniture"},
    {"PRODUCT": "Server Rack", "PRICE": 2200.00, "ORDERDATE": "01-11-2025", "ID": "104", "COSTCENTER": "Data Infrastructure"},
]

CLASSIFICATION_COLUMNS = {
    "PRODUCT": ["Couch", "Office Chair", "Server Rack"],
    "PRICE": [999.99, 150.8, 2200.00],
    "ORDERDATE": ["28-11-2025", "02-11-2025", "01-11-2025"],
    "ID": ["35", "44", "104"],
    "COSTCENTER": ["[PREDICT]", "Office Furniture", "Data Infrastructure"],
}

REGRESSION_ROWS = [
    {"PRODUCT": "Couch", "PRICE": 999.99, "ORDERDATE": "28-11-2025", "ID": "35", "DISCOUNT_RATE": "[PREDICT]"},
    {"PRODUCT": "Office Chair", "PRICE": 150.80, "ORDERDATE": "02-11-2025", "ID": "44", "DISCOUNT_RATE": 0.12},
    {"PRODUCT": "Server Rack", "PRICE": 2200.00, "ORDERDATE": "01-11-2025", "ID": "104", "DISCOUNT_RATE": 0.05},
    {"PRODUCT": "Standing Desk", "PRICE": 640.00, "ORDERDATE": "05-11-2025", "ID": "205", "DISCOUNT_RATE": 0.10},
    {"PRODUCT": "Monitor 27 inch", "PRICE": 289.99, "ORDERDATE": "08-11-2025", "ID": "306", "DISCOUNT_RATE": "[PREDICT]"},
]

REGRESSION_SCHEMA = {
    "PRODUCT": DataType(dtype="string"),
    "PRICE": DataType(dtype="numeric"),
    "ORDERDATE": DataType(dtype="date"),
    "ID": DataType(dtype="string"),
    "DISCOUNT_RATE": DataType(dtype="numeric"),
}


def predict_by_rows():
    """
    Classify a target column using row-oriented input data.

    Context rows supply known COSTCENTER values; the query row marked
    with "[PREDICT]" receives a predicted classification.

    Returns:
        The prediction result.
    """
    client = RPTClient()
    body = RPTRequest(
        prediction_config=PredictionConfig(
            target_columns=[
                TargetColumn(
                    name="COSTCENTER",
                    prediction_placeholder="[PREDICT]",
                    task_type="classification",
                )
            ]
        ),
        index_column="ID",
        rows=CLASSIFICATION_ROWS,
        data_schema=CLASSIFICATION_SCHEMA,
    )
    return client.predict(body=body, model_name=MODEL_NAME)


def predict_by_columns():
    """
    Classify a target column using column-oriented input data.

    Equivalent to predict_by_rows but uses the columns format instead of rows.

    Returns:
        The prediction result.
    """
    client = RPTClient()
    body = RPTRequest(
        prediction_config=PredictionConfig(
            target_columns=[
                TargetColumn(
                    name="COSTCENTER",
                    prediction_placeholder="[PREDICT]",
                    task_type="classification",
                )
            ]
        ),
        columns=CLASSIFICATION_COLUMNS,
        data_schema=CLASSIFICATION_SCHEMA,
    )
    return client.predict(body=body, model_name=MODEL_NAME)


def regression():
    """
    Predict a numeric target column (regression).

    Rows with "[PREDICT]" in DISCOUNT_RATE receive a predicted numeric value.

    Returns:
        The prediction result.
    """
    client = RPTClient()
    body = RPTRequest(
        prediction_config=PredictionConfig(
            target_columns=[TargetColumn(name="DISCOUNT_RATE", task_type="regression")]
        ),
        index_column="ID",
        rows=REGRESSION_ROWS,
        data_schema=REGRESSION_SCHEMA,
    )
    return client.predict(body=body, model_name=MODEL_NAME)