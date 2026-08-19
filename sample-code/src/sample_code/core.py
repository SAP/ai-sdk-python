from typing import Annotated

from ai_api_client_sdk.models.parameter_binding import ParameterBinding
from ai_core_sdk.ai_core_v2_client import AICoreV2Client
from fastapi import Body


def get_configurations():
    """
    Get all configurations for the resource group specified in the .env file.

    Returns:
        A dict containing the configurations in a ConfigurationQueryResponse object.
    """
    client = AICoreV2Client.from_env()
    return client.configuration.query()


def create_configuration():
    """
    Create configuration for GPT-5.4-nano.

    The configuration is created for the resource group specified in the .env file.
    """
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
    """
    Get all deployments for the resource group specified in the .env file.

    Returns:
        A dict containing the deployments in a DeploymentQueryResponse object.
    """
    client = AICoreV2Client.from_env()
    return client.deployment.query()


def create_deployment(configuration_id: Annotated[str, Body(embed=True)]):
    """
    Create deployment for the configuration_id in the request body.

    The deployment is created for the resource group specified in the .env file.
    """
    client = AICoreV2Client.from_env()
    return client.deployment.create(configuration_id=configuration_id)


def get_scenarios():
    """
    Get all scenarios.

    Returns:
        A dict containing the scenarios in a ScenarioQueryResponse object.
    """
    client = AICoreV2Client.from_env()
    return client.scenario.query()


def get_models():
    """
    Get all available models.

    Returns:
        A dict containing the models in a ModelQueryResponse object.
    """
    client = AICoreV2Client.from_env()
    return client.model.query()
