import argparse

from gen_ai_hub.prompt_registry.client import PromptTemplateClient
from gen_ai_hub.prompt_registry.models.prompt_template import PromptTemplateGetResponse


### ENVIRONMENT VARIABLES --- SET IF NECESSARY ###
# os.environ["AICORE_AUTH_URL"] = "https://mlfwdftest.authentication.sap.hana.ondemand.com/oauth/token"
# os.environ["AICORE_BASE_URL"] = "https://api.ai.internalprod.eu-central-1.aws.ml.hana.ondemand.com/v2"
# os.environ["AICORE_RESOURCE_GROUP"] = "default"
# os.environ["AICORE_CLIENT_ID"] = "<client-id>"
# os.environ["AICORE_CLIENT_SECRET"] = "<client-secret>"
###

def delete_prompt_template(prompt_template:PromptTemplateGetResponse, scenario:str, dry_run:bool):
    """
    Delete all versions of a given prompt template for a specific scenario.

    Args:
        prompt_template (PromptTemplateGetResponse): The prompt template object to delete.
        scenario (str): The scenario associated with the template.
        dry_run (bool): If True, perform a dry run without actual deletion.
    """
    template_history = client.get_prompt_template_history(scenario=scenario,
                                                          name=prompt_template.name,
                                                          version=prompt_template.version)
    print(f"Deleting test prompt template versions for template '{prompt_template.name}'."
          f" Found {len(template_history.resources)} versions.")
    for history_version in template_history.resources:
        delete_history_version(history_version, client, dry_run)

def delete_history_version(history_version:PromptTemplateGetResponse,
                           prompt_template_client:PromptTemplateClient,
                           dry_run:bool):
    """
    Delete a specific version of a prompt template if it is not the head version.

    Args:
        history_version (PromptTemplateGetResponse): The version of the prompt template to delete.
        prompt_template_client (PromptTemplateClient): The client used to interact with the prompt template API.
        dry_run (bool): If True, perform a dry run without actual deletion.
    """
    version = history_version.version
    name = history_version.name
    scenario = history_version.scenario
    if not history_version.is_version_head:
        if not dry_run:
            prompt_template_client.delete_prompt_template_by_id(history_version.id)
        prefix = "DRY RUN:" if dry_run else ""
        print(f"{prefix} Deleted prompt template version: "
              f"name={name}, "
              f"version={version}, "
              f"scenario={scenario}, "
              f"id={history_version.id}")
    else:
        print(f"Skipping deletion of the head version: "
              f"name={name}, "
              f"version={version}, "
              f"scenario={scenario}, "
              f"id={history_version.id}")

if __name__ == "__main__":
    """
    Main script to clean up prompt templates for a specified scenario.

    This script retrieves all prompt templates for the given scenario and deletes
    their versions, except for the head version.

    Command-line Arguments:
        --scenario_name (str): The scenario name to process. Default is "test_scenario".
        --delete (str): "True" or "False" to indicate if templates should be deleted. Default is "false".
    """
    parser = argparse.ArgumentParser(description="Cleanup script for prompt templates.")
    parser.add_argument("--scenario_name",
                        required=False,
                        help="The scenario name to process.",
                        default="test_scenario")
    parser.add_argument("--delete",
                        required=False,
                        help="True or False to indicate if templates should be deleted",
                        default="false")
    args = parser.parse_args()
    scenario_name = args.scenario_name
    dry_run = args.delete.lower() == "false"

    client = PromptTemplateClient()
    templates = client.get_prompt_templates(scenario=scenario_name, name=None, version=None)
    print(f"Deleting test prompt templates for scenario '{scenario_name}'."
          f" Found {len(templates.resources)} templates.")
    for template in templates.resources:
        delete_prompt_template(template, scenario_name, dry_run)
