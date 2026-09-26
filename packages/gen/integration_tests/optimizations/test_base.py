"""Base test class for optimization integration tests."""
import os
import unittest

from gen_ai_hub.optimizations.client import OptimizationClient


class OptimizationClientTestBase(unittest.TestCase):
    """Base class for optimization client integration tests."""

    @classmethod
    def setUpClass(cls):
        """Set up the test class with credentials."""
        cls.base_url = os.getenv("AICORE_BASE_URL")
        cls.auth_url = os.getenv("AICORE_AUTH_URL")
        cls.client_id = os.getenv("AICORE_CLIENT_ID")
        cls.client_secret = os.getenv("AICORE_CLIENT_SECRET")
        cls.resource_group = "default"
        cls.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        cls.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        cls.dataset_path = os.path.abspath(os.path.join(current_dir, "po_dataset_small.json"))

    def setUp(self):
        """Set up each test with a fresh optimization client instance and object store secrets."""
        self.client = OptimizationClient(
            base_url=self.base_url,
            auth_url=self.auth_url,
            client_id=self.client_id,
            client_secret=self.client_secret,
            resource_group=self.resource_group,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        )

        AWS_S3_ENDPOINT = "s3-eu-central-1.amazonaws.com"
        AWS_BUCKET_ID = "hcp-e597ff51-40f5-42c9-a75a-744281742e61"
        AWS_REGION = "eu-central-1"

        default_secret_creds = {
            "data": {},
            "type": "S3",
            "pathPrefix": "sdkOutputFiles",
            "endpoint": AWS_S3_ENDPOINT,
            "bucket": AWS_BUCKET_ID,
            "region": AWS_REGION,
            "usehttps": "1",
        }

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

        self.client.setup(
            default_secret_body=default_secret_creds,
            input_secret_body=input_secret_creds,
            replace_existing=True,
        )
