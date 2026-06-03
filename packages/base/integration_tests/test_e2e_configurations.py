from .ai_api_v2_client_e2e_test_base import AIAPIV2ClientE2ETestBase


class TestE2EConfigurations(AIAPIV2ClientE2ETestBase):

    def test_configurations(self):
        n = 3
        configuration_dicts = []
        executable_d = self.get_an_executable(deployable=True)
        configuration_dicts.extend(self.create_configuration_dicts(n=n, executable_id=executable_d.id,
                                                                   parameters=executable_d.parameters,
                                                                   input_artifacts=executable_d.input_artifacts))
        executable_e = self.get_an_executable(deployable=False)
        configuration_dicts.extend(self.create_configuration_dicts(n=n, executable_id=executable_e.id,
                                                                   parameters=executable_e.parameters))
        for configuration_dict in configuration_dicts:
            res = self.ai_api_v2_client.configuration.create(**configuration_dict)
            self.assertIsNotNone(res.id)
            configuration_dict['id'] = res.id

        res = self.ai_api_v2_client.configuration.query(scenario_id=self.test_scenario_id)
        self.assertTrue(res.count >= 2 * n)
        self.assert_dicts_in_objects(configuration_dicts, res.resources)
        self.assert_datetime(res.resources[0].created_at)

        res_count = self.ai_api_v2_client.configuration.count(scenario_id=self.test_scenario_id)
        self.assertTrue(res_count >= 2 * n)

        res = self.ai_api_v2_client.configuration.query(executable_ids=[executable_e.id, executable_d.id])
        self.assertTrue(res.count >= 2 * n)
        self.assert_dicts_in_objects(configuration_dicts, res.resources)

        res_count = self.ai_api_v2_client.configuration.count(executable_ids=[executable_e.id, executable_d.id])
        self.assertTrue(res_count >= 2 * n)

        res = self.ai_api_v2_client.configuration.query(executable_ids=[executable_e.id])
        self.assertTrue(res.count >= n)
        self.assert_dicts_in_objects(configuration_dicts[n:], res.resources)

        res_count = self.ai_api_v2_client.configuration.count(executable_ids=[executable_e.id])
        self.assertTrue(res_count >= n)

        search_string = 'Test Configuration'
        res = self.ai_api_v2_client.configuration.query(scenario_id=self.test_scenario_id, search=search_string)
        self.assertTrue(res.count >= 2 * n)
        self.assertTrue(all(search_string in c.name for c in res.resources))

        res_count = self.ai_api_v2_client.configuration.count(scenario_id=self.test_scenario_id, search=search_string)
        self.assertTrue(res_count >= 2 * n)

        configuration_dict = configuration_dicts[n - 1]
        configuration = self.ai_api_v2_client.configuration.get(configuration_id=configuration_dict['id'])
        self.assert_object(configuration_dict, configuration)
        self.assert_datetime(configuration.created_at)

    def test_configuration_with_expand_scenario(self):
        n = 3
        configuration_dicts = []
        executable_d = self.get_an_executable()
        configuration_dicts.extend(self.create_configuration_dicts(n=n, executable_id=executable_d.id,
                                                                   parameters=executable_d.parameters,
                                                                   input_artifacts=executable_d.input_artifacts))

        for configuration_dict in configuration_dicts:
            res = self.ai_api_v2_client.configuration.create(**configuration_dict)
            self.assertIsNotNone(res.id)
            configuration_dict['id'] = res.id

        res = self.ai_api_v2_client.configuration.query(scenario_id=self.test_scenario_id, expand='scenario')
        self.assertTrue(res.count >= n)
        self.assert_dicts_in_objects(configuration_dicts, res.resources)
        self.assertTrue('scenario' in a for a in res.resources)

        configuration_dict = configuration_dicts[n - 1]
        configuration = self.ai_api_v2_client.configuration.get(configuration_id=configuration_dict['id'],
                                                                expand='scenario')
        self.assert_object(configuration_dict, configuration)
        self.assertIsNotNone(configuration.scenario)
        self.assertIsNotNone(configuration.scenario.id)
        self.assertIsNotNone(configuration.scenario.name)
        self.assertIsNotNone(configuration.scenario.created_at)
        self.assertIsNotNone(configuration.scenario.modified_at)
