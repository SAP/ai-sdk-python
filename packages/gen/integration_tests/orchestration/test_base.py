import time
import unittest
from uuid import uuid4

from gen_ai_hub.proxy import get_proxy_client

shared_api_url = None


def get_shared_api_url():
    global shared_api_url
    if shared_api_url is None:
        shared_api_url = initialize_orchestration_service()
    return shared_api_url


def initialize_orchestration_service():
    client = get_proxy_client(proxy_version="gen-ai-hub").ai_core_client
    deployment = get_or_create_deployment(client)
    return deployment.deployment_url


def get_or_create_deployment(client, timeout=600):
    deployments = client.deployment.query(scenario_id="orchestration").resources
    deployments = [d for d in deployments if d.status.value == "RUNNING"]

    if deployments:
        return deployments[0]

    config = get_or_create_configuration(client)
    deployment_id = client.deployment.create(configuration_id=config.id).id

    deployment = client.deployment.get(deployment_id)
    start = time.time()
    while deployment.status.value != "RUNNING":
        if time.time() - start > timeout:
            raise TimeoutError("Timeout waiting for deployment to start.")
        deployment = client.deployment.get(deployment_id)
        time.sleep(10)

    return deployment


def get_or_create_configuration(client):
    configs = client.configuration.query(scenario_id="orchestration").resources
    if configs:
        return configs[0]

    return client.configuration.create(
        scenario_id="orchestration",
        executable_id="orchestration",
        name=f"orchestration-config-{str(uuid4())[:8]}",
    )


class OrchestrationServiceTestBase(unittest.TestCase):

    def setUp(self):
        self.api_url = get_shared_api_url()
        self.assertIsNotNone(self.api_url)
