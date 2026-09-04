from gen_ai_hub.tab_ai_orchestration import TabAiOrchestrationClient
from gen_ai_hub.tab_ai_orchestration.generated.models.context_selection_config import ContextSelectionConfig
from gen_ai_hub.tab_ai_orchestration.generated.models.model_rpt15 import ModelRpt15
from gen_ai_hub.tab_ai_orchestration.generated.models.model_rpt15_explanations import ModelRpt15Explanations
from gen_ai_hub.tab_ai_orchestration.generated.models.model_rpt15_prediction_config import ModelRpt15PredictionConfig
from gen_ai_hub.tab_ai_orchestration.generated.models.modelconfig import Modelconfig
from gen_ai_hub.tab_ai_orchestration.generated.models.predict_request import PredictRequest
from gen_ai_hub.tab_ai_orchestration.generated.models.prediction_config import PredictionConfig
from gen_ai_hub.tab_ai_orchestration.generated.models.target_column import TargetColumn
from gen_ai_hub.tab_ai_orchestration.generated.models.task_type_enum import TaskTypeEnum
from gen_ai_hub.tab_ai_orchestration.generated.models.tfm_enum import TFMEnum


async def predict():
    """
    Make a tabular prediction using the Tabular AI Orchestration service.

    Returns:
        JSON object containing the prediction response.
    """
    request = PredictRequest(
        model_name=TFMEnum.SAP_MINUS_RPT_MINUS_1_MINUS_SMALL,
        scenario_config_name="product-prediction-scenario-lowercase",
        context_selection_config=ContextSelectionConfig(
            num_rows=3,
            strategy="random",
            index_column="id",
        ),
        prediction_config=PredictionConfig(
            target_columns=[
                TargetColumn(
                    name="salesgroup",
                    prediction_placeholder="[PREDICT]",
                    task_type=TaskTypeEnum.CLASSIFICATION,
                )
            ]
        ),
        columns={
            "product": ["Laptop", "Office Chair"],
            "price": [999.99, 142.99],
            "date": ["2025-01-15", "2025-07-12"],
            "id": ["35", "571"],
            "salesgroup": ["[PREDICT]", "[PREDICT]"],
        },
    )

    async with TabAiOrchestrationClient(model_name="sap-rpt-1-small") as client:
        response = await client.predict(
            ai_resource_group="default",
            predict_request=request,
        )

    return response.to_dict()


async def predict_with_explanations():
    """
    Make a tabular prediction with explanations using the Tabular AI Orchestration service.

    Returns:
        JSON object containing the prediction response with top column scores and
        relevant context rows for each prediction.
    """
    request = PredictRequest(
        model_name=TFMEnum.SAP_MINUS_RPT_MINUS_1_DOT_5,
        scenario_config_name="product-prediction-scenario-lowercase",
        context_selection_config=ContextSelectionConfig(
            num_rows=3,
            strategy="random",
            index_column="id",
        ),
        prediction_config=PredictionConfig(
            target_columns=[
                TargetColumn(
                    name="salesgroup",
                    prediction_placeholder="[PREDICT]",
                    task_type=TaskTypeEnum.CLASSIFICATION,
                )
            ]
        ),
        var_model_config=Modelconfig(ModelRpt15(
            index_column="id",
            data_schema={
                "product": {"dtype": "string"},
                "price": {"dtype": "numeric"},
                "date": {"dtype": "date"},
                "id": {"dtype": "string"},
                "salesgroup": {"dtype": "string"},
            },
            prediction_config=ModelRpt15PredictionConfig(
                explanations=ModelRpt15Explanations(
                    top_column_scores=3,
                    top_relevant_context_rows=2,
                )
            ),
        )),
        columns={
            "product": ["Laptop", "Office Chair"],
            "price": [999.99, 142.99],
            "date": ["2025-01-15", "2025-07-12"],
            "id": ["35", "571"],
            "salesgroup": ["[PREDICT]", "[PREDICT]"],
        },
    )

    async with TabAiOrchestrationClient(model_name="sap-rpt-1.5") as client:
        response = await client.predict(
            ai_resource_group="default",
            predict_request=request,
        )

    return response.to_dict()
