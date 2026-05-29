import uuid

from ai_api_client_sdk.models.base_models import BasicModifyRequest
from ai_api_client_sdk.models.status import Status
from ai_api_client_sdk.models.target_status import TargetStatus
from .ai_api_v2_client_e2e_test_base import AIAPIV2ClientE2ETestBase


class TestE2EDeployments(AIAPIV2ClientE2ETestBase):
    def test_deployments(self):
        configuration = self.get_a_configuration(deployable=True)
        n = 2
        deployment_dicts = []
        for _ in range(n):
            res = self.ai_api_v2_client.deployment.create(configuration_id=configuration.id)
            deployment_dicts.append({
                'id': res.id,
                'configuration_id': configuration.id,
                'configuration_name': configuration.name,
                'scenario_id': self.test_scenario_id
            })
        for dep_dict in deployment_dicts:
            dep = self.ai_api_v2_client.deployment.get(deployment_id=dep_dict['id'])
            self.assert_object(dep_dict, dep)
            self.assert_datetime(dep.created_at)
            dep_dict['created_at'] = dep.created_at
            self.assert_datetime(dep.modified_at)
            self.assertEqual(TargetStatus.RUNNING, dep.target_status)
            dep_dict['target_status'] = dep.target_status
            dep = self.wait_until_enactment_has_status(resource_client=self.ai_api_v2_client.deployment,
                                                       params={'deployment_id': dep_dict['id']}, status=Status.RUNNING)
            dep_dict['status'] = dep.status
            self.assertIsNotNone(dep.deployment_url)
            self.assertNotEqual('', dep.deployment_url)
            dep_dict['deployment_url'] = dep.deployment_url

            dep = self.ai_api_v2_client.deployment.get(deployment_id=dep_dict['id'], select='status')
            self.assertEqual(dep_dict['status'], dep.status)
            self.assertFalse(hasattr(dep, dep_dict['deployment_url']))
            self.assertFalse(hasattr(dep, dep_dict['configuration_name']))

            logs = self.ai_api_v2_client.deployment.query_logs(deployment_id=dep_dict['id'])
            self.assertIsNotNone(logs.data.result)

        res = self.ai_api_v2_client.deployment.query(scenario_id=self.test_scenario_id,
                                                     configuration_id=configuration.id,
                                                     executable_ids=[configuration.executable_id],
                                                     status=Status.RUNNING)
        self.assertTrue(res.count >= n)
        self.assert_datetime(res.resources[0].created_at)
        self.assert_dicts_in_objects(deployment_dicts, res.resources)

        res_count = self.ai_api_v2_client.deployment.count(scenario_id=self.test_scenario_id,
                                                           configuration_id=configuration.id,
                                                           executable_ids=[configuration.executable_id],
                                                           status=Status.RUNNING)
        self.assertTrue(res_count >= n)

        # modify deployment with new configuration_id
        dep_dict = deployment_dicts[0]
        new_conf = self.get_a_configuration(deployable=True)
        self.ai_api_v2_client.deployment.modify(deployment_id=dep_dict['id'], configuration_id=new_conf.id)
        dep = self.ai_api_v2_client.deployment.get(deployment_id=dep_dict['id'])
        self.assertEqual(new_conf.id, dep.configuration_id)
        self.assertEqual(configuration.id, dep.latest_running_configuration_id)
        dep = self.wait_until_enactment_has_status(resource_client=self.ai_api_v2_client.deployment,
                                                   params={'deployment_id': dep_dict['id']}, status=Status.RUNNING)
        self.assertEqual(Status.RUNNING, dep.status)
        self.assertIsNotNone(dep.deployment_url)
        self.assertNotEqual('', dep.deployment_url)

        # bulk modify deployments
        deployments = [
            BasicModifyRequest(deployment_dicts[0]['id'], TargetStatus.STOPPED),
            BasicModifyRequest(str(uuid.uuid4()), TargetStatus.STOPPED)
        ]
        dep_bulk_modify_response = self.ai_api_v2_client.deployment.bulk_modify(deployments=deployments)
        self.assertEqual("Deployment modification scheduled", dep_bulk_modify_response.deployments[0].message)
        self.assertEqual("01010016", dep_bulk_modify_response.deployments[1].error.code)

    def test_deployments_with_ttl(self):
        configuration = self.get_a_configuration(deployable=True)
        ttl = "10h"
        res = self.ai_api_v2_client.deployment.create(configuration_id=configuration.id, ttl=ttl)
        dep_dict = {
            'id': res.id,
            'configuration_id': configuration.id,
            'configuration_name': configuration.name,
            'scenario_id': self.test_scenario_id
        }
        dep = self.ai_api_v2_client.deployment.get(deployment_id=res.id)
        self.assert_object(dep_dict, dep)
        self.assertIsNotNone(dep.ttl)
        self.assertEqual(dep.ttl, ttl)
