from gen_ai_hub.prompt_registry.client import OrchestrationConfigClient, PromptTemplateClient
from gen_ai_hub.prompt_registry.models.prompt_template import PromptTemplate, PromptTemplateSpec
from gen_ai_hub.orchestration_v2.models.config import ModuleConfig, OrchestrationConfig
from gen_ai_hub.orchestration_v2.models.llm_model_details import LLMModelDetails
from gen_ai_hub.orchestration_v2.models.message import SystemMessage, UserMessage
from gen_ai_hub.orchestration_v2.models.template import PromptTemplatingModuleConfig, Template

SCENARIO = "my-scenario"
TEMPLATE_NAME = "my-template"
VERSION = "1.0.0"
CONFIG_NAME = "my-orchestration-config"


def create_prompt_template():
    """
    Create a prompt template with a user-input placeholder.

    The placeholder {{ ?user_input }} will be substituted at runtime via fill_prompt_template.
    """
    client = PromptTemplateClient()
    spec = PromptTemplateSpec(
        template=[
            PromptTemplate(role="system", content="You are a helpful assistant."),
            PromptTemplate(role="user", content="Hello World!"),
        ]
    )
    return client.create_prompt_template(
        scenario=SCENARIO,
        name=TEMPLATE_NAME,
        version=VERSION,
        prompt_template_spec=spec,
    )


def get_prompt_templates():
    """List all prompt templates matching the scenario/name/version filter."""
    client = PromptTemplateClient()
    return client.get_prompt_templates(scenario=SCENARIO, name=TEMPLATE_NAME, version=VERSION)


def delete_prompt_template(template_id: str):
    """Delete a prompt template by its ID."""
    client = PromptTemplateClient()
    return client.delete_prompt_template_by_id(template_id)


def create_orchestration_config():
    """
    Create an orchestration config that bundles an LLM and a prompt template.

    The config references gpt-4o-mini and a static Hello World prompt.
    """
    client = OrchestrationConfigClient()
    spec = OrchestrationConfig(
        modules=ModuleConfig(
            prompt_templating=PromptTemplatingModuleConfig(
                prompt=Template(
                    template=[
                        SystemMessage(content="You are a helpful assistant."),
                        UserMessage(content="Hello, World!"),
                    ]
                ),
                model=LLMModelDetails(name="gpt-4o-mini"),
            )
        )
    )
    return client.create_orchestration_config(
        scenario=SCENARIO,
        name=CONFIG_NAME,
        version=VERSION,
        spec=spec,
    )


def get_orchestration_configs():
    """List orchestration configs matching the scenario/name/version filter."""
    client = OrchestrationConfigClient()
    return client.get_orchestration_configs(
        scenario=SCENARIO,
        name=CONFIG_NAME,
        version=VERSION,
        include_spec=True,
    )
