from typing import Annotated

from ai_api_client_sdk.models.parameter_binding import ParameterBinding
from ai_core_sdk.ai_core_v2_client import AICoreV2Client
from fastapi import Body


def get_configurations():
    client = AICoreV2Client.from_env()
    return client.configuration.query()


def create_configuration():
    client = AICoreV2Client.from_env()
    parameter_bindings = [
        ParameterBinding.from_dict({"key": "modelName", "value": "gpt-5.4-nano"}),
        ParameterBinding.from_dict({"key": "modelVersion", "value": "latest"}),
    ]
    return client.configuration.create(
        name="my-gpt-5.4-nano-config",
        scenario_id="foundation-models",
        executable_id="azure-openai",
        parameter_bindings=parameter_bindings,
        input_artifact_bindings=[],
    )


def get_deployments():
    client = AICoreV2Client.from_env()
    return client.deployment.query()


def create_deployment(configuration_id: Annotated[str, Body(embed=True)]):
    client = AICoreV2Client.from_env()
    return client.deployment.create(configuration_id=configuration_id)


def get_scenarios():
    client = AICoreV2Client.from_env()
    return client.scenario.query()


def get_models():
    client = AICoreV2Client.from_env()
    return client.model.query()
