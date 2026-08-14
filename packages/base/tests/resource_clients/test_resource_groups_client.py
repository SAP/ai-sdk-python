from ai_api_client_sdk.models.resource_group import ResourceGroup
from ai_api_client_sdk.models.resource_group_query_response import ResourceGroupQueryResponse
from ai_api_client_sdk.resource_clients.resource_groups_client import ResourceGroupsClient
from .resource_client_test_base import ResourceClientTestBase


class TestDockerRegistrySecretsClient(ResourceClientTestBase):
    def setUp(self):
        super().setUp()
        self.client = ResourceGroupsClient(self.rest_client_mock)
        self.rg_path = '/admin/resourceGroups'

    def assert_resource_group(self, rg_expected: ResourceGroup, rg: ResourceGroup):
        self.assertEqual(rg_expected.resource_group_id, rg.resource_group_id)
        self.assertEqual(rg_expected.labels, rg.labels)
        self.assertEqual(rg_expected.status, rg.status)
        self.assertEqual(rg_expected.created_at, rg.created_at)

    @staticmethod
    def create_resource_group_dict():
        return {
            'resource_group_id': 'testrg',
            'labels': [
                {
                    'key': 'ext.ai.sap.com/label1',
                    'value': 'value1',
                },
                {
                    'key': 'ext.ai.sap.com/label2',
                    'value': 'value2',
                },
            ],
            'status': 'test_status',
            'created_at': '2021-03-29T12:58:05Z'
        }

    @staticmethod
    def create_resource_group():
        return ResourceGroup.from_dict(TestDockerRegistrySecretsClient.create_resource_group_dict())

    def test_create_resource_group(self):
        self.rest_client_mock.post.return_value = self.create_resource_group_dict()
        rg = self.create_resource_group()
        response = self.client.create(resource_group_id=rg.resource_group_id, labels=rg.labels)
        body = {
            'resourceGroupId': rg.resource_group_id,
            'labels': [l.to_dict() for l in rg.labels],
        }
        self.rest_client_mock.post.assert_called_with(path=self.rg_path, body=body)
        self.assert_resource_group(rg, response)

    def test_delete_resource_group(self):
        test_rg_name = 'test_resource_group_name'
        response_dict = {
            'id': test_rg_name,
            'message': 'Resource Group deleted',
        }
        self.rest_client_mock.delete.return_value = response_dict
        br = self.client.delete(resource_group_id=test_rg_name)
        self.rest_client_mock.delete.assert_called_with(path=f'{self.rg_path}/{test_rg_name}')
        self.assertEqual(response_dict['id'], br.id)
        self.assertEqual(response_dict['message'], br.message)

    def test_get_resource_group(self):
        rg_dict = self.create_resource_group_dict()
        resource_group_id = rg_dict['resource_group_id']
        self.rest_client_mock.get.return_value = rg_dict.copy()
        rg = self.client.get(resource_group_id=resource_group_id)
        self.rest_client_mock.get.assert_called_with(path=f'{self.rg_path}/{resource_group_id}')

        expected_rg = self.create_resource_group()
        self.assert_resource_group(expected_rg, rg)
        self.assertIn("Resource group id: ", rg.__str__())
        self.assertIn(rg_dict['resource_group_id'], rg.__str__())

    def test_get_resource_group_aicore(self):
        rg_dict = self.create_resource_group_dict()
        resource_group_id = rg_dict['resource_group_id']
        mock_rg = rg_dict.copy()
        mock_rg['zoneId'] = 'test-zone-id'
        self.rest_client_mock.get.return_value = mock_rg
        rg = self.client.get(resource_group_id=resource_group_id)
        self.rest_client_mock.get.assert_called_with(path=f'{self.rg_path}/{resource_group_id}')

        expected_rg = self.create_resource_group()
        self.assert_resource_group(expected_rg, rg)

    def test_modify_resource_group(self):
        rg = self.create_resource_group()
        self.rest_client_mock.modify.return_value = ""
        self.client.modify(resource_group_id=rg.resource_group_id, labels=rg.labels)
        body = {
            'labels': [l.to_dict() for l in rg.labels],
        }
        self.rest_client_mock.patch.assert_called_with(path=f'{self.rg_path}/{rg.resource_group_id}', body=body)

    def test_query_resource_group(self):
        self.rest_client_mock.get.return_value = {
            'resources': [
                self.create_resource_group_dict(),
            ],
            'count': 1,
        }
        response = self.client.query()
        self.rest_client_mock.get.assert_called_with(path=f'{self.rg_path}', params=None)

        expected_response = ResourceGroupQueryResponse([self.create_resource_group()], 1)
        self.assertEqual(expected_response.count, response.count)
        self.assertEqual(len(expected_response.resources), len(response.resources))

        self.assert_resource_group(expected_response.resources[0], response.resources[0])

    def test_query_resource_group_search_case_insensitive(self):
        self.rest_client_mock.get.return_value = {
            'resources': [
                self.create_resource_group_dict(),
            ],
            'count': 1,
        }
        params = {'search': 'test_search', 'search_case_insensitive': True}
        response = self.client.query(**params)

        params['$search'] = params['search']
        del params['search']
        self.rest_client_mock.get.assert_called_with(path=f'{self.rg_path}', params=params)

        expected_response = ResourceGroupQueryResponse([self.create_resource_group()], 1)
        self.assertEqual(expected_response.count, response.count)
        self.assertEqual(len(expected_response.resources), len(response.resources))

        self.assert_resource_group(expected_response.resources[0], response.resources[0])
