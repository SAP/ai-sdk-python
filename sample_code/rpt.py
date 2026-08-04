"""Service logic for RPT 1.5 predictions — mirrors sample-code/src/rpt.ts."""

import os
from typing import Any

from gen_ai_hub import GenAIHubProxyClient
from gen_ai_hub.proxy.native.rpt_1_5 import (
    PredictionConfig,
    PredictionPlaceholder,
    RPT15Client,
    TargetColumnConfig,
    rows_request,
)

MODEL_NAME = os.environ.get("RPT_MODEL_NAME", "sap-rpt-1.5")

_REQUEST = rows_request(
    prediction_config=PredictionConfig(
        target_columns=[
            TargetColumnConfig(
                name="SALESGROUP",
                prediction_placeholder=PredictionPlaceholder("[PREDICT]"),
            )
        ]
    ),
    index_column="__row_idx__",
    rows=[
        {
            "PRODUCT": "Laptop",
            "PRICE": 999.99,
            "PRODUCTION_DATE": "2025-01-15",
            "__row_idx__": "35",
            "SALESGROUP": "[PREDICT]",
        },
        {
            "PRODUCT": "Office Chair",
            "PRICE": 142.99,
            "PRODUCTION_DATE": "2025-07-13",
            "__row_idx__": "571",
            "SALESGROUP": "[PREDICT]",
        },
        {
            "PRODUCT": "Desktop Computer",
            "PRICE": 921.50,
            "PRODUCTION_DATE": "2024-12-02",
            "__row_idx__": "42",
            "SALESGROUP": "Electronics",
        },
        {
            "PRODUCT": "Macbook",
            "PRICE": 1220.99,
            "PRODUCTION_DATE": "2026-01-31",
            "__row_idx__": "99",
            "SALESGROUP": "Electronics",
        },
        {
            "PRODUCT": "Office Desk",
            "PRICE": 750.50,
            "PRODUCTION_DATE": "2024-12-05",
            "__row_idx__": "689",
            "SALESGROUP": "Furniture",
        },
    ],
)

async def predict_sales_group(proxy_client: GenAIHubProxyClient) -> Any:
    """Predict the sales group of products."""
    client = RPT15Client(model_name=MODEL_NAME, proxy_client=proxy_client)
    response = await client.predict(_REQUEST)
    return response["predictions"]  # type: ignore[index]


async def rpt_health(proxy_client: GenAIHubProxyClient) -> Any:
    """Check the health of the RPT deployment."""
    client = RPT15Client(model_name=MODEL_NAME, proxy_client=proxy_client)
    return await client.health()
