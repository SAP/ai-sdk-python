"""
Shared base for batch service integration tests.

Provides a BatchService instance already wired to the live AI Core backend.
The service URL is resolved once (via the proxy client's base_url) and shared
across all test classes in the session.
"""

import os
import unittest

from time import sleep

from gen_ai_hub import GenAIHubProxyClient
from gen_ai_hub.proxy import get_proxy_client
from gen_ai_hub.batch_service.models.response import BatchStatus
from gen_ai_hub.batch_service.service import BatchService

AWS_ACCESS_KEY_ID = "AWS_ACCESS_KEY_ID"
AWS_SECRET_ACCESS_KEY = "AWS_SECRET_ACCESS_KEY"
AWS_BUCKET_NAME = "AWS_BUCKET_NAME"
AWS_HOST = "AWS_HOST"
AWS_REGION = "AWS_REGION"
AICORE_RESOURCE_GROUP = "AICORE_RESOURCE_GROUP"


class BatchServiceTestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proxy_client: GenAIHubProxyClient = get_proxy_client('gen-ai-hub')
        cls.service = BatchService(proxy_client=cls.proxy_client)
        cls.secret_name = 'batch-service-oss'
        cls.input_uri = f"ai://{cls.secret_name}/batch_service_test_data/requests.jsonl"
        cls.output_uri = f"ai://{cls.secret_name}/batch_service_test_data/output/"
        cls.provider = "azure-openai"
        cls.model = "gpt-4.1"
        cls.create_object_store_secret()

    def wait_for_batch_to_be_deletable(self, batch_id: str, timeout=300, polling_interval=5):
        status = None
        deletable_statuses = [BatchStatus.COMPLETED, BatchStatus.FAILED, BatchStatus.CANCELLED]
        while status not in deletable_statuses and timeout != 0:
            sleep(polling_interval)
            response = self.service.get_status(batch_id=batch_id)
            status = response.current_status
            timeout -= polling_interval

    @classmethod
    def create_object_store_secret(cls):
        aws_access_key_id = os.environ.get(AWS_ACCESS_KEY_ID)
        aws_secret_access_key = os.environ.get(AWS_SECRET_ACCESS_KEY)
        response = cls.proxy_client.ai_core_client.object_store_secrets.create(
            name=cls.secret_name,
            type="S3",
            data={
                AWS_ACCESS_KEY_ID: aws_access_key_id,
                AWS_SECRET_ACCESS_KEY: aws_secret_access_key,
            },
            bucket=os.environ.get(AWS_BUCKET_NAME),
            endpoint=os.environ.get(AWS_HOST),
            region=os.environ.get(AWS_REGION),
            resource_group=os.environ.get(AICORE_RESOURCE_GROUP),
        )

