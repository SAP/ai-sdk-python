from typing import List

from ai_api_client_sdk.models.scenario import Scenario
from .ai_api_v2_client_e2e_test_base import AIAPIV2ClientE2ETestBase


class TestE2EScenarios(AIAPIV2ClientE2ETestBase):

    @staticmethod
    def _get_scenario_from_scenarios(scenarios: List[Scenario], scenario_id: str):
        for s in scenarios:
            if s.id == scenario_id:
                return s
        return None

    def test_query_and_get_scenarios(self):
        response = self.ai_api_v2_client.scenario.query()
        scenarios = response.resources
        self.assertEqual(response.count, len(scenarios))
        queried_scenario = self._get_scenario_from_scenarios(scenarios, self.test_scenario_id)
        scenario = self.ai_api_v2_client.scenario.get(scenario_id=self.test_scenario_id)
        self.assertEqual(queried_scenario, scenario)
        self.assertIsNotNone(scenario.id)
        self.assertIsNotNone(scenario.name)
        self.assert_datetime(scenario.created_at)
        self.assert_datetime(scenario.modified_at)

    def test_query_and_get_scenarios_for_llm(self):
        response = self.ai_api_v2_client.scenario.query(only_llm_scenarios=True)
        scenarios = response.resources
        self.assertEqual(response.count, len(scenarios))
        llm_scenario_id = 'foundation-models'
        queried_scenario = self._get_scenario_from_scenarios(scenarios, llm_scenario_id)
        scenario = self.ai_api_v2_client.scenario.get(scenario_id=llm_scenario_id)
        self.assertEqual(queried_scenario, scenario)
        self.assertIsNotNone(scenario.id)
        self.assertIsNotNone(scenario.name)
        self.assert_datetime(scenario.created_at)
        self.assert_datetime(scenario.modified_at)
        self.assertIsNotNone(scenario.labels)

    def test_query_llm_scenarios(self):
        response = self.ai_api_v2_client.scenario.query_llm_scenarios()
        scenarios = response.resources
        self.assertEqual(response.count, len(scenarios))
        scenario = scenarios[0]
        self.assertIsNotNone(scenario.id)
        self.assertIsNotNone(scenario.name)
        self.assert_datetime(scenario.created_at)
        self.assert_datetime(scenario.modified_at)
        self.assertIsNotNone(scenario.labels)

    def test_query_versions(self):
        version_response = self.ai_api_v2_client.scenario.query_versions(scenario_id=self.test_scenario_id)
        self.assertTrue(version_response.count > 0)
        self.assertEqual(version_response.count, len(version_response.resources))
        version = version_response.resources[0]
        self.assertIsNotNone(version.id)
        self.assertIsNotNone(version.scenario_id)
        self.assert_datetime(version.created_at)
        self.assert_datetime(version.modified_at)

    def test_is_llm_scenario(self):
        llm_scenario_id = 'foundation-models'
        scenario = self.ai_api_v2_client.scenario.get(scenario_id=llm_scenario_id)
        self.assertTrue(scenario.is_llm_scenario())
        scenario = self.ai_api_v2_client.scenario.get(scenario_id=self.test_scenario_id)
        self.assertFalse(scenario.is_llm_scenario())
