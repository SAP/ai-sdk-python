from typing import List

from .ai_api_v2_client_e2e_test_base import AIAPIV2ClientE2ETestBase


class TestE2EMeta(AIAPIV2ClientE2ETestBase):

    def assert_attributes_not_none(self, obj: object, attributes: List[str]):
        for a in attributes:
            self.assertIsNotNone(getattr(obj, a))

    def assert_attributes_true(self, obj: object, attributes: List[str]):
        for a in attributes:
            self.assertTrue(getattr(obj, a))

    def test_meta(self):
        capabilities = self.ai_api_v2_client.meta.get()
        self.assert_attributes_not_none(capabilities, ['ai_api', 'runtime_identifier', 'runtime_api_version'])
        self.assert_attributes_not_none(capabilities.ai_api, ['capabilities', 'limits', 'version'])
        self.assert_attributes_not_none(capabilities.ai_api.capabilities, ['logs', 'multitenant','bulk_updates'])
        self.assert_attributes_true(capabilities.ai_api.capabilities,
                                    ['user_executions', 'shareable', 'static_deployments', 'user_deployments',
                                     'time_to_live_deployments', 'execution_schedules'])
        self.assert_attributes_true(capabilities.ai_api.capabilities.bulk_updates, ['executions', 'deployments'])
        self.assert_attributes_true(capabilities.ai_api.capabilities.logs, ['deployments', 'executions'])
        self.assert_attributes_not_none(capabilities.ai_api.limits, ['deployments', 'executions'])
        self.assertEqual(capabilities.ai_api.limits.executions.max_running_count, -1)
        self.assertEqual(capabilities.ai_api.limits.deployments.max_running_count, -1)

    def test_versions(self):
        version_list = self.ai_api_v2_client.meta.get_versions()
        self.assertIsNotNone(version_list.versions)
        self.assert_attributes_not_none(version_list.versions[0], ['version_id', 'url', 'description'])
