import time

from ai_api_client_sdk.models.label import Label
from ai_api_client_sdk.models.resource_group import ResourceGroup
from . import get_random_string
from .ai_api_v2_client_e2e_test_base import AIAPIV2ClientE2ETestBase


class TestE2EResourceGroup(AIAPIV2ClientE2ETestBase):

    @staticmethod
    def _get_resource_group(resource_group_id: str):
        return {
            'resource_group_id': resource_group_id,
            'labels': [
                Label(key="ext.ai.sap.com/label1", value="value1"),
                Label(key="ext.ai.sap.com/label2", value="value2"),
            ],
        }

    def create_resource_group(self, resource_group_id: str):
        rg_dict = self._get_resource_group(resource_group_id)
        response = self.ai_api_v2_client.resource_groups.create(
            resource_group_id=rg_dict['resource_group_id'],
            labels=rg_dict['labels'])
        self.assertEqual(rg_dict['resource_group_id'], response.resource_group_id)
        # During create, the resource group labels are not returned, so we can not test them here.

    def delete_resource_group(self, resource_group_id: str):
        response = self.ai_api_v2_client.resource_groups.delete(
            resource_group_id=resource_group_id)
        self.assertEqual(resource_group_id, response.id)
        self.assertIsNotNone(response.message)

    def get_resource_group(self, resource_group_id: str):
        # Poll until the resource group's status becomes PROVISIONED or until timeout.
        timeout_seconds = 60
        poll_interval = 2
        deadline = time.time() + timeout_seconds
        response = None
        while time.time() <= deadline:
            response = self.ai_api_v2_client.resource_groups.get(
                resource_group_id=resource_group_id)
            if response.status == 'PROVISIONED':
                break
            time.sleep(poll_interval)
        # The resource group should reach PROVISIONED status within the timeout.
        self.assertEqual('PROVISIONED', response.status)
        rg_dict = self._get_resource_group(resource_group_id)
        # We can only be sure about these two fields.
        self.assertEqual(rg_dict['resource_group_id'], response.resource_group_id)
        self.assertEqual(rg_dict['labels'], response.labels)
        # The next fields have values that are not influenced by us.
        # However, these values must exist.
        self.assertIsNotNone(response.status)
        self.assert_datetime(response.created_at)

    def modify_resource_group(self, resource_group_id: str):
        labels = [
            Label(key="ext.ai.sap.com/label10", value="value10"),
        ]

        self.ai_api_v2_client.resource_groups.modify(
            resource_group_id=resource_group_id,
            labels=labels)

        # Poll until the resource groups' lables changed or until timeout.
        timeout_seconds = 60
        poll_interval = 2
        deadline = time.time() + timeout_seconds
        response = None
        while time.time() <= deadline:
            response = self.ai_api_v2_client.resource_groups.get(
                resource_group_id=resource_group_id)
            if {l.key: l.value for l in labels} == {l.key: l.value for l in response.labels}:
                break
            time.sleep(poll_interval)
        # Check that the modification was sucessfull.
        self.assertEqual({l.key: l.value for l in labels}, {l.key: l.value for l in response.labels})

    def query_resource_group(self):
        response = self.ai_api_v2_client.resource_groups.query()
        self.assertGreaterEqual(response.count, 1)
        self.assertGreaterEqual(len(response.resources), 1)
        self.assertIsInstance(response.resources[0], ResourceGroup)
        self.assert_datetime(response.resources[0].created_at)

    def test_resource_groups(self):
        resource_group_id = f'trg{get_random_string()[:5]}'
        self.create_resource_group(resource_group_id)
        self.get_resource_group(resource_group_id)
        self.query_resource_group()
        self.modify_resource_group(resource_group_id)
        time.sleep(3)
        self.delete_resource_group(resource_group_id)
