from ai_api_client_sdk.models.base_models import BasicModifyRequest
from ai_api_client_sdk.models.status import Status
from ai_api_client_sdk.models.target_status import TargetStatus
from .ai_api_v2_client_e2e_test_base import AIAPIV2ClientE2ETestBase


class TestE2EExecutions(AIAPIV2ClientE2ETestBase):
    def test_executions(self):
        configuration = self.get_a_configuration(deployable=False)
        n = 3
        execution_dicts = []
        for _ in range(n):
            res = self.ai_api_v2_client.execution.create(configuration_id=configuration.id)
            execution_dicts.append({
                'id': res.id,
                'configuration_id': configuration.id,
                'configuration_name': configuration.name,
                'scenario_id': self.test_scenario_id
            })
        for execution_dict in execution_dicts:
            execution = self.ai_api_v2_client.execution.get(execution_id=execution_dict['id'])
            self.assert_object(execution_dict, execution)
            self.assert_datetime(execution.created_at)
            execution_dict['created_at'] = execution.created_at
            self.assert_datetime(execution.modified_at)
            self.assertEqual(TargetStatus.COMPLETED, execution.target_status)
            execution_dict['target_status'] = execution.target_status
            execution = self.wait_until_enactment_has_status(resource_client=self.ai_api_v2_client.execution,
                                                             params={'execution_id': execution_dict['id']},
                                                             status=Status.COMPLETED)
            execution_dict['status'] = execution.status

            exc = self.ai_api_v2_client.execution.get(execution_id=execution_dict['id'], select='status')
            self.assertEqual(execution_dict['status'], exc.status)
            self.assertFalse(hasattr(exc, execution_dict['configuration_name']))
            self.assertFalse(hasattr(exc, execution_dict['scenario_id']))

            logs = self.ai_api_v2_client.execution.query_logs(execution_id=execution_dict['id'])
            self.assertIsNotNone(logs.data.result)

        res = self.ai_api_v2_client.execution.query(scenario_id=self.test_scenario_id,
                                                    configuration_id=configuration.id,
                                                    executable_ids=[configuration.executable_id],
                                                    status=Status.COMPLETED)
        self.assertTrue(res.count >= n)
        self.assert_dicts_in_objects(execution_dicts, res.resources)

        res_count = self.ai_api_v2_client.execution.count(scenario_id=self.test_scenario_id,
                                                          configuration_id=configuration.id,
                                                          executable_ids=[configuration.executable_id],
                                                          status=Status.COMPLETED)
        self.assertTrue(res_count >= n)

        # bulk modify executions
        executions = [
            BasicModifyRequest(execution_dicts[0]['id'], TargetStatus.DELETED),
            BasicModifyRequest("exec_a_not_exist", TargetStatus.DELETED)
        ]
        response = self.ai_api_v2_client.execution.bulk_modify(executions=executions)
        self.assertEqual("Execution modification scheduled", response.executions[0].message)
        self.assertEqual("01010020", response.executions[1].error.code)
