from .ai_api_v2_client_e2e_test_base import AIAPIV2ClientE2ETestBase


class TestE2EExecutables(AIAPIV2ClientE2ETestBase):
    def test_query_and_get_executables(self):
        res = self.ai_api_v2_client.executable.query(scenario_id=self.test_scenario_id)
        self.assertEqual(res.count, len(res.resources))
        self.assertTrue(res.count > 0)
        executables = res.resources
        self.assert_datetime(executables[0].created_at)
        executable = self.ai_api_v2_client.executable.get(scenario_id=executables[0].scenario_id,
                                                          executable_id=executables[0].id)
        self.assertEqual(executables[0], executable)
        self.assertIsNotNone(executable.id)
        self.assertIsNotNone(executable.scenario_id)
        self.assertIsNotNone(executable.version_id)
        self.assertIsNotNone(executable.name)
        self.assertIsNotNone(executable.deployable)
        self.assert_datetime(executable.created_at)
        self.assert_datetime(executable.modified_at)
