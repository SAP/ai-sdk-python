from gen_ai_hub.prompt_registry.client import OrchestrationConfigClient, PromptTemplateClient
from gen_ai_hub.prompt_registry.models.prompt_template import PromptTemplate, PromptTemplateSpec
from gen_ai_hub.orchestration_v2.models.config import ModuleConfig, OrchestrationConfig
from gen_ai_hub.orchestration_v2.models.llm_model_details import LLMModelDetails
from gen_ai_hub.orchestration_v2.models.message import SystemMessage, UserMessage
from gen_ai_hub.orchestration_v2.models.template import PromptTemplatingModuleConfig, Template

def create_prompt_template():
    """
    Create a prompt template with a user-input placeholder.

    The placeholder {{?user_input}} will be substituted at runtime via fill_prompt_template.

    Returns:
        The created prompt template.
    """
    client = PromptTemplateClient()
    spec = PromptTemplateSpec(
        template=[
            PromptTemplate(role="system", content="You are a helpful assistant."),
            PromptTemplate(role="user", content="{{?user_input}}"),
        ]
    )
    return client.create_prompt_template(
        scenario="my-scenario",
        name="my-template",
        version="1.0.0",
        prompt_template_spec=spec,
    )


def fill_prompt_template():
    """
    Fill the prompt template placeholders with concrete values.

    Replaces the {{?user_input}} placeholder in the template with a concrete question.

    Returns:
        The filled prompt response.
    """
    client = PromptTemplateClient()
    return client.fill_prompt_template(
        scenario="my-scenario",
        name="my-template",
        version="1.0.0",
        input_params={"user_input": "What are the main features of SAP BTP?"},
    )


def get_prompt_templates():
    """
    List all prompt templates matching the scenario/name/version filter.

    Returns:
        List of matching prompt templates.
    """
    client = PromptTemplateClient()
    return client.get_prompt_templates(scenario="my-scenario", name="my-template", version="1.0.0")


def delete_prompt_template(template_id: str):
    """
    Delete a prompt template by its ID.

    Args:
        template_id: The ID of the prompt template to delete.

    Returns:
        HTTP response confirming deletion with HTTP status code 204.
    """
    client = PromptTemplateClient()
    return client.delete_prompt_template_by_id(template_id)


def create_orchestration_config():
    """
    Create an orchestration config that bundles an LLM and a prompt template.

    The config references gpt-5.4-nano and a static Hello World prompt.

    Returns:
        The created orchestration config.
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
                model=LLMModelDetails(name="gpt-5.4-nano"),
            )
        )
    )
    return client.create_orchestration_config(
        scenario="my-scenario",
        name="my-orchestration-config",
        version="1.0.0",
        spec=spec,
    )


def get_orchestration_configs():
    """
    List orchestration configs matching the scenario/name/version filter.

    Returns:
        List of matching orchestration configs.
    """
    client = OrchestrationConfigClient()
    return client.get_orchestration_configs(
        scenario="my-scenario",
        name="my-orchestration-config",
        version="1.0.0",
        include_spec=True,
    )
