from ai_api_client_sdk.models.status import ScheduleStatus
from .ai_api_v2_client_e2e_test_base import AIAPIV2ClientE2ETestBase


class TestE2EExecutionSchedules(AIAPIV2ClientE2ETestBase):
    def test_execution_schedules(self):
        es_name = 'test execution schedule'
        es_cron = '1 1 1 1 1'
        configuration = self.get_a_configuration(deployable=False)

        # *** create ***
        res = self.ai_api_v2_client.execution_schedule.create(name=es_name, cron=es_cron,
                                                              configuration_id=configuration.id)
        es_dict = {
            'id': res.id,
            'configuration_id': configuration.id,
            'cron': es_cron,
            'name': es_name
        }
        execution_schedule = self.ai_api_v2_client.execution_schedule.get(execution_schedule_id=res.id)
        self.assert_datetime(execution_schedule.created_at)
        self.assert_datetime(execution_schedule.modified_at)
        self.assert_object(es_dict, execution_schedule)

        # *** modify ***
        es_dict['cron'] = '0 0 * * *'
        es_dict['status'] = ScheduleStatus.INACTIVE
        res_mod = self.ai_api_v2_client.execution_schedule.modify(execution_schedule_id=res.id,
                                                                  cron=es_dict['cron'],
                                                                  status=es_dict['status']
                                                                  )
        self.assertEqual(res_mod.id, res.id)
        self.assertIn("modified", res_mod.message)
        execution_schedule = self.ai_api_v2_client.execution_schedule.get(execution_schedule_id=res.id)
        self.assert_datetime(execution_schedule.modified_at)
        es_dict['modified_at'] = execution_schedule.modified_at
        self.assert_object(es_dict, execution_schedule)

        # *** query ***
        es_name2 = es_name + '2'
        configuration2 = self.get_a_configuration(deployable=False)
        res2 = self.ai_api_v2_client.execution_schedule.create(name=es_name2, cron=es_cron,
                                                               configuration_id=configuration2.id)
        res_qry = self.ai_api_v2_client.execution_schedule.query(top=10)
        self.assertEqual(res_qry.count, 2)
        self.assert_datetime(res_qry.resources[0].created_at)

        execution_schedule2 = self.ai_api_v2_client.execution_schedule.get(execution_schedule_id=res2.id)
        self.assert_datetime(execution_schedule2.created_at)
        es_dict2 = {
            'id': res2.id,
            'configuration_id': configuration2.id,
            'cron': es_cron,
            'name': es_name2,
            'status': ScheduleStatus.ACTIVE,
            'created_at': execution_schedule2.created_at
        }
        self.assert_dicts_in_objects([es_dict, es_dict2], res_qry.resources)

        # *** count ***
        res_count = self.ai_api_v2_client.execution_schedule.count(status=ScheduleStatus.INACTIVE)
        self.assertEqual(res_count, 1)

        # *** delete ***
        res_del = self.ai_api_v2_client.execution_schedule.delete(execution_schedule_id=res2.id)
        self.assertEqual(res_del.id, res2.id)
        self.assertIn("deleted", res_del.message)
