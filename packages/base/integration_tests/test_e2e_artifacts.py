from ai_api_client_sdk.models.artifact import Artifact
from ai_api_client_sdk.models.label import Label
from .ai_api_v2_client_e2e_test_base import AIAPIV2ClientE2ETestBase


class TestE2EArtifacts(AIAPIV2ClientE2ETestBase):

    def test_artifacts(self):
        n = 3
        artifact_dicts = self.create_artifact_dicts(n)
        for ad in artifact_dicts:
            res = self.ai_api_v2_client.artifact.create(**ad)
            self.assertIsNotNone(res.id)
            ad['id'] = res.id

        res = self.ai_api_v2_client.artifact.query(scenario_id=self.test_scenario_id)
        self.assertTrue(res.count >= n)
        self.assert_dicts_in_objects(artifact_dicts, res.resources)
        self.assert_datetime(res.resources[0].created_at)

        search_string = 'Test Artifact'
        res = self.ai_api_v2_client.artifact.query(scenario_id=self.test_scenario_id, search=search_string)
        self.assertTrue(all(search_string in a.name or search_string in a.description for a in res.resources))

        artifact_dict = artifact_dicts[n - 1]
        artifact = self.ai_api_v2_client.artifact.get(artifact_id=artifact_dict['id'])
        self.assert_object(artifact_dict, artifact)
        self.assert_datetime(artifact.created_at)
        self.assert_datetime(artifact.modified_at)

        res_count = self.ai_api_v2_client.artifact.count(scenario_id=self.test_scenario_id)
        self.assertTrue(res_count >= n)

    def test_artifact_with_expand_scenario(self):
        n = 3
        artifact_dicts = self.create_artifact_dicts(n)
        for ad in artifact_dicts:
            res = self.ai_api_v2_client.artifact.create(**ad)
            self.assertIsNotNone(res.id)
            ad['id'] = res.id

        res = self.ai_api_v2_client.artifact.query(scenario_id=self.test_scenario_id, expand='scenario')
        self.assertTrue(res.count >= n)
        self.assert_dicts_in_objects(artifact_dicts, res.resources)
        self.assertTrue('scenario' in a for a in res.resources)

        artifact_dict = artifact_dicts[n - 1]
        artifact = self.ai_api_v2_client.artifact.get(artifact_id=artifact_dict['id'], expand='scenario')
        self.assert_object(artifact_dict, artifact)
        self.assertIsNotNone(artifact.scenario)
        self.assertIsNotNone(artifact.scenario.id)
        self.assertIsNotNone(artifact.scenario.name)
        self.assert_datetime(artifact.scenario.created_at)
        self.assert_datetime(artifact.scenario.modified_at)

    def test_artifact_kind_other(self):
        ad = self.create_artifact_dict(1, kind=Artifact.Kind.OTHER)
        res = self.ai_api_v2_client.artifact.create(**ad)
        self.assertIsNotNone(res.id)

        ad['id'] = res.id

        artifact = self.ai_api_v2_client.artifact.get(artifact_id=ad['id'])
        self.assert_object(ad, artifact)

    def test_filter_artifacts_by_labels(self):
        artifact_dicts = [
            self.create_artifact_dict(labels=[Label(**{'key': 'ext.ai.sap.com/s4hana-version', 'value': 'string'})]),
            self.create_artifact_dict(labels=[Label(**{'key': 'ext.ai.sap.com/s4hana-version', 'value': 'string2'}),
                                              Label(**{'key': 'ext.ai.sap.com/dummy', 'value': 'dummy'})]),
            self.create_artifact_dict(labels=[Label(**{'key': 'ext.ai.sap.com/s4hana-version', 'value': 'string2'})])
        ]
        for artifact_dict in artifact_dicts:
            res = self.ai_api_v2_client.artifact.create(**artifact_dict)
            self.assertIsNotNone(res.id)
            artifact_dict['id'] = res.id

        res = self.ai_api_v2_client.artifact.query(scenario_id=self.test_scenario_id,
                                                   artifact_label_selector='ext.ai.sap.com/s4hana-version=string')
        self.assertTrue(res.count >= 1)
        self.assertEqual(res.count, len(res.resources))
        res_ids = [artifact.id for artifact in res.resources]
        self.assertIn(artifact_dicts[0]['id'], res_ids)
        self.assertNotIn(artifact_dicts[1]['id'], res_ids)
        self.assertNotIn(artifact_dicts[2]['id'], res_ids)

        res_count = self.ai_api_v2_client.artifact.count(scenario_id=self.test_scenario_id,
                                                         artifact_label_selector='ext.ai.sap.com/s4hana-version=string2')
        self.assertTrue(res_count >= 1)

        res = self.ai_api_v2_client.artifact.query(scenario_id=self.test_scenario_id,
                                                   artifact_label_selector='ext.ai.sap.com/s4hana-version=string2')
        self.assertTrue(res.count >= 1)
        self.assertEqual(res.count, len(res.resources))
        res_ids = [artifact.id for artifact in res.resources]
        self.assertIn(artifact_dicts[1]['id'], res_ids)
        self.assertIn(artifact_dicts[2]['id'], res_ids)
        self.assertNotIn(artifact_dicts[0]['id'], res_ids)

        res_count = self.ai_api_v2_client.artifact.count(scenario_id=self.test_scenario_id,
                                                         artifact_label_selector='ext.ai.sap.com/s4hana-version=string2')
        self.assertTrue(res_count >= 1)

        res = self.ai_api_v2_client.artifact.query(scenario_id=self.test_scenario_id,
                                                   artifact_label_selector='ext.ai.sap.com/s4hana-version=string2,ext.ai.sap.com/dummy=dummy')
        self.assertTrue(res.count >= 1)
        res_ids = [artifact.id for artifact in res.resources]
        self.assertIn(artifact_dicts[1]['id'], res_ids)
        self.assertNotIn(artifact_dicts[0]['id'], res_ids)
        self.assertNotIn(artifact_dicts[2]['id'], res_ids)

        res_count = self.ai_api_v2_client.artifact.count(scenario_id=self.test_scenario_id,
                                                         artifact_label_selector='ext.ai.sap.com/s4hana-version=string2,ext.ai.sap.com/dummy=dummy')
        self.assertTrue(res_count >= 1)

        res = self.ai_api_v2_client.artifact.query(scenario_id=self.test_scenario_id,
                                                   artifact_label_selector='ext.ai.sap.com/dummy!=dummy')
        self.assertEqual(res.count, len(res.resources))
        res_ids = [artifact.id for artifact in res.resources]
        for artifact in artifact_dicts:
            self.assertNotIn(artifact['id'], res_ids)

        res_count = self.ai_api_v2_client.artifact.count(scenario_id=self.test_scenario_id,
                                                         artifact_label_selector='ext.ai.sap.com/dummy!=dummy')
        self.assertEqual(res_count, len(res.resources))
