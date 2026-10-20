"""
Base test class for evaluation integration tests.
Provides common setup and utilities for evaluation client tests.
"""
import unittest
from gen_ai_hub.evaluations.client import EvaluationClient
import os


class EvaluationClientTestBase(unittest.TestCase):
    """Base class for evaluation client integration tests."""

    @classmethod
    def setUpClass(cls):
        """Set up the test class with credentials."""
        # Hardcoded credentials (will be moved to environment variables later)
        cls.base_url = os.getenv("AICORE_BASE_URL")
        cls.auth_url = os.getenv("AICORE_AUTH_URL")
        cls.client_id = os.getenv("AICORE_CLIENT_ID")
        cls.client_secret = os.getenv("AICORE_CLIENT_SECRET")
        cls.resource_group = "default"
        cls.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        cls.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        cls.input_object_store_secret_name = "sdk-data"
        current_dir = os.path.dirname(os.path.abspath(__file__))
        cls.dataset_path = os.path.abspath(os.path.join(current_dir, 'eval-data', 'testdata', 'medicalqna_dataset.csv'))

    def setUp(self):
        """Set up each test with a fresh evaluation client instance and object store secrets."""
        self.client = EvaluationClient(
            base_url=self.base_url,
            auth_url=self.auth_url,
            client_id=self.client_id,
            client_secret=self.client_secret,
            resource_group=self.resource_group,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            input_object_store_secret_name=self.input_object_store_secret_name,
        )

        # Setup S3 credentials for object store secrets
        AWS_S3_ENDPOINT = "s3-eu-central-1.amazonaws.com"
        AWS_BUCKET_ID = "hcp-e597ff51-40f5-42c9-a75a-744281742e61"
        AWS_REGION = "eu-central-1"

        # default secret is needed to store output artifacts that the evaluation job creates after it is completed
        default_secret_creds = {
            "data": {},
            "type": "S3",
            "pathPrefix": "sdkOutputFiles",
            "endpoint": AWS_S3_ENDPOINT,
            "bucket": AWS_BUCKET_ID,
            "region": AWS_REGION,
            "usehttps": "1",
        }

        # input secret is used to load input artifacts required by the evaluation job.
        # This is optional as these files can be loaded via default secret path as well.
        input_secret_creds = {
            "data": {},
            "name": "sdk-data",
            "type": "S3",
            "pathPrefix": "sdk_input_files/data",
            "endpoint": AWS_S3_ENDPOINT,
            "bucket": AWS_BUCKET_ID,
            "region": AWS_REGION,
            "usehttps": "1",
        }

        # Creation of object store secrets and creates orchestration deployment url if not passed via initialization.
        response = self.client.setup(
            default_secret_body=default_secret_creds,
            input_secret_body=input_secret_creds,
            replace_existing=True
        )
        self.client.orchestration_url = response.get("orchestration_url")
