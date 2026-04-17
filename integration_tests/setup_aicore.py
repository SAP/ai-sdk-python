from __future__ import annotations

import time
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, ClassVar, Dict, List, Optional

from ai_api_client_sdk.models.parameter_binding import ParameterBinding
from ai_api_client_sdk.models.status import Status
from ai_core_sdk.ai_core_v2_client import AICoreV2Client

from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client, proxy_version_context

FOUNDATION_MODEL_SCENARIO = 'foundation-models'


@dataclass
class FoundationalModelExecutable:
    _instances: ClassVar[Dict[str, 'FoundationalModelExecutable']] = {}
    _model_to_scenario: ClassVar[Dict[str, 'FoundationalModelExecutable']] = {}
    _discovered: ClassVar[bool] = False

    id_: str
    model_version_default: Optional[str] = None
    models: List[str] = field(default_factory=list)

    def __post_init__(self):
        # Assign a unique ID and store the instance
        FoundationalModelExecutable._instances[self.id_] = self
        for model in self.models:
            FoundationalModelExecutable._model_to_scenario[model] = self

    @classmethod
    def get_instance(cls, scenario_id: str) -> FoundationalModelExecutable:
        # Retrieve an instance by its ID
        return cls._instances.get(scenario_id)

    @classmethod
    def get_executable(cls, model_name: str) -> FoundationalModelExecutable:
        # Retrieve an instance by its ID
        return cls._model_to_scenario.get(model_name)

    @classmethod
    def discover(cls, client: AICoreV2Client, scenario_id: str = FOUNDATION_MODEL_SCENARIO, force: bool = False):
        if cls._discovered and not force:
            return
        execs = client.executable.query(scenario_id=scenario_id)
        for exe in execs.resources:
            models = None
            model_version_default = None
            for param in exe.parameters:
                if param.name == 'modelName':
                    models = []
                    if param.description is not None:
                        models = [m.strip() for m in param.description.partition(':')[-1].split(',')]
                    if param.default and param.default not in models:
                        models.append(param.default)
                if param.name == 'modelVersion':
                    model_version_default = param.default
            cls(
                id_=exe.id,
                model_version_default=model_version_default,
                models=models,
            )
        cls._discovered = True


def find_existing_config(client, executable_id, params, scenario_id=FOUNDATION_MODEL_SCENARIO):
    parameter_values_new = {p.key: p.value for p in params}
    configs = client.configuration.query(
        scenario_id=scenario_id)
    for config in configs.resources:
        if config.executable_id != executable_id:
            continue
        parameter_values = {p.key: p.value for p in config.parameter_bindings}
        parameter_values['name'] = config.name
        if parameter_values == parameter_values_new:
            return config


def get_deployments(ai_core_client, status=(Status.PENDING, Status.RUNNING, Status.UNKNOWN), **kwargs):
    if isinstance(status, Status):
        status = [status]
    deployments = []
    for status_ in status:
        deployments.extend(
            ai_core_client.deployment.query(
                **{**kwargs, 'status': status_}
            ).resources)
    return deployments


def deploy(ai_core_client: AICoreV2Client,
           model_name: str,
           model_version: Optional[str] = None,
           config_name: Optional[str] = None,
           executable_id: Optional[str] = None,
           scenario_id: str = FOUNDATION_MODEL_SCENARIO,
           force: bool = False):
    FoundationalModelExecutable.discover(ai_core_client, scenario_id=scenario_id)

    config_name = model_name
    params = [ParameterBinding(
        key='modelName',
        value=model_name,
    )]
    if model_version:
        config_name = f'{model_name}-{model_version}'
        params.append(ParameterBinding(
            key='modelVersion',
            value=model_version,
        ))

    params.append(ParameterBinding(
        key='name',
        value=config_name,
    ))

    executable = find_executable(model_name=model_name, executable_id=executable_id)
    config = find_existing_config(ai_core_client, executable.id_, params, scenario_id=scenario_id)
    if config is None:
        config_name = config_name or f'{model_name}-{model_version or "default"}'
        config = ai_core_client.configuration.create(
            scenario_id=FOUNDATION_MODEL_SCENARIO,
            executable_id=executable.id_,
            name=config_name,
            parameter_bindings=params,
        )
    deployments = get_deployments(ai_core_client, scenario_id=scenario_id, configuration_id=config.id)
    if len(deployments) > 0 and not force:
        return False, deployments[0], config
    return True, ai_core_client.deployment.create(configuration_id=config.id), config


def find_executable(model_name: str, executable_id: Optional[str] = None):
    if executable_id is None:
        executable = FoundationalModelExecutable.get_executable(model_name)
    else:
        try:
            executable = FoundationalModelExecutable.get_instance(executable_id)
        except KeyError:
            executable = FoundationalModelExecutable(id_=executable_id, models=[model_name])

    if executable is None:
        raise ValueError(f"Executable not found for model '{model_name}'.")

    return executable


def get_bedrock_models():
    """Return list of bedrock models (Amazon and Anthropic models available via Bedrock)"""
    return [
        ("amazon--titan-embed-image", "latest"),
        ("amazon--titan-embed-text", "latest"),
        ("amazon--nova-micro", "latest"),
        ("amazon--nova-lite", "latest"),
        ("amazon--nova-pro", "latest"),
        ("amazon--nova-premier", "latest"),
        ("anthropic--claude-3-haiku", "latest"),
        ("anthropic--claude-4-opus", "latest"),
        ("anthropic--claude-3.5-sonnet", "latest"),
        ("anthropic--claude-3.7-sonnet", "latest"),
        ("anthropic--claude-4-sonnet", "latest"),
        ("anthropic--claude-4.5-haiku", "latest"),
    ]


def get_standard_models():
    """Return list of standard models (non-bedrock models)"""
    return [
        ("gpt-4o", "latest"),
        ("gpt-4o-mini", "latest"),
        ("gpt-4.1", "latest"),
        ("gpt-4.1-mini", "latest"),
        ("gpt-4.1-nano", "latest"),
        ("gpt-5", "latest"),
        ("gpt-5-mini", "latest"),
        ("gpt-5-nano", "latest"),
        ("o1", "latest"),
        ("o3", "latest"),
        ("o3-mini", "latest"),
        ("o4-mini", "latest"),
        ("mistralai--mistral-small-instruct", "latest"),
        ("mistralai--mistral-medium-instruct", "latest"),
        ("mistralai--mistral-large-instruct", "latest"),
        ("nvidia--llama-3.2-nv-embedqa-1b", "latest"),
        ("text-embedding-3-small", "latest"),
        ("text-embedding-3-large", "latest"),
        ("text-embedding-ada-002", "latest"),
        ("gemini-2.0-flash", "latest"),
        ("gemini-2.0-flash-lite", "latest"),
        ("gemini-2.5-flash", "latest"),
        ("gemini-2.5-flash-lite", "latest"),
        ("gemini-2.5-pro", "latest"),
        ("gemini-embedding", "latest"),
        ("sonar", "latest"),
        ("sonar-pro", "latest"),
        ("cohere--command-a-reasoning", "latest"),
        ("cohere--reranker", "latest"),
        ("sap-rpt-1-small","latest"),
    ]


def _setup_models(client: AICoreV2Client, models: List[tuple], max_wait_seconds=600):
    """Internal function to setup a specific list of models"""
    running_deployments = []
    pending_deployments = []
    deployment_id_to_model = {}
    
    for model, model_version in models:
        try:
            newly_deployed, deployment, _ = deploy(ai_core_client=client, model_name=model, model_version=model_version)
            if newly_deployed or deployment.status in (Status.PENDING, Status.UNKNOWN):
                pending_deployments.append(deployment)
            else:
                running_deployments.append(deployment)
            deployment_id_to_model[deployment.id] = model
        except Exception as e:
            print(f"Error for virtual deployment of model {model}-{model_version}: {e}")
            continue  # Skip model if it is not available
    
    if pending_deployments:
        check_pending_deployments(client, max_wait_seconds, pending_deployments, running_deployments)

    return {deployment_id_to_model[dep.id]: dep for dep in running_deployments}


def check_pending_deployments(client: AICoreV2Client, max_wait_seconds: int, pending_deployments: list[Any],
                              running_deployments: list[Any]):
    checked_deployments = []
    start = time.time()
    while pending_deployments or checked_deployments:
        if time.time() - start > max_wait_seconds:
            raise TimeoutError('Timeout waiting for deployments to start.')
        dep = pending_deployments.pop(0)
        dep = client.deployment.get(dep.id)
        if dep.status == Status.RUNNING:
            running_deployments.append(dep)
        else:
            checked_deployments.append(dep)
        if len(pending_deployments) == 0:
            pending_deployments = checked_deployments
            checked_deployments = []
            time.sleep(10)


@lru_cache
def setup_bedrock_models(client: AICoreV2Client, max_wait_seconds=600):
    """Setup only bedrock models (Amazon and Anthropic models)"""
    bedrock_models = get_bedrock_models()
    return _setup_models(client, bedrock_models, max_wait_seconds)


@lru_cache
def setup_standard_models(client: AICoreV2Client, max_wait_seconds=600):
    """Setup only standard (non-bedrock) models"""
    standard_models = get_standard_models()
    return _setup_models(client, standard_models, max_wait_seconds)


@lru_cache
def setup_aicore_instance(client: AICoreV2Client, max_wait_seconds=600):
    """Setup all models (for backward compatibility)"""
    all_models = get_bedrock_models() + get_standard_models()
    return _setup_models(client, all_models, max_wait_seconds)


class TestCaseAICoreSetupMixin:
    """Base mixin for AI Core setup - sets up all models"""
    @classmethod
    def setUpClass(cls):  # noqa: N802 - unittest framework method name
        with proxy_version_context('gen-ai-hub'):
            cls.proxy_client = get_proxy_client()
        cls.aicore_deployments = setup_aicore_instance(cls.proxy_client.ai_core_client)


class TestCaseBedrockSetupMixin:
    """Mixin specifically for bedrock tests - sets up only bedrock models"""
    @classmethod
    def setUpClass(cls):  # noqa: N802 - unittest framework method name
        with proxy_version_context('gen-ai-hub'):
            cls.proxy_client = get_proxy_client()
        cls.aicore_deployments = setup_bedrock_models(cls.proxy_client.ai_core_client)


class TestCaseStandardSetupMixin:
    """Mixin specifically for standard tests - sets up only standard models"""
    @classmethod
    def setUpClass(cls):  # noqa: N802 - unittest framework method name
        with proxy_version_context('gen-ai-hub'):
            cls.proxy_client = get_proxy_client()
        cls.aicore_deployments = setup_standard_models(cls.proxy_client.ai_core_client)
