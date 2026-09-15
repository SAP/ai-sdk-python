"""Sample: Tabular AI Orchestration predictions using the Kiota-generated client.

The Kiota client exposes a request-builder tree. After running `make generate-kiota`,
the generated root client (`TabAiOrchestrationClient`) exposes:

    client.generated.predict.post(body)          # POST /predict
    client.generated.predict.with_http_info(...)  # raw response

The request and response models live under:
    gen_ai_hub.tab_ai_orchestration_kiota.generated.models.*
"""

from gen_ai_hub.tab_ai_orchestration_kiota import KiotaTabAiOrchestrationClient


async def predict():
    from gen_ai_hub.tab_ai_orchestration_kiota.generated.models.predict_request import (
        PredictRequest,
    )

    async with KiotaTabAiOrchestrationClient(model_name="sap-rpt-1.5") as client:
        body = PredictRequest()
        # Populate body fields as required by your deployment's schema.
        # See gen_ai_hub.tab_ai_orchestration_kiota.generated.models for all model classes.
        result = await client.generated.predict.post(body)
    return {"result": result}


async def predict_with_explanations():
    from gen_ai_hub.tab_ai_orchestration_kiota.generated.models.predict_request import (
        PredictRequest,
    )
    from gen_ai_hub.tab_ai_orchestration_kiota.generated.models.context_selection_config import (
        ContextSelectionConfig,
    )

    async with KiotaTabAiOrchestrationClient(model_name="sap-rpt-1.5") as client:
        body = PredictRequest()
        context_config = ContextSelectionConfig()
        body.context_selection_config = context_config
        result = await client.generated.predict.post(body)
    return {"result": result}
