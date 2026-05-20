import copy
import uuid

from ai_api_client_sdk.helpers.datetime_parser import parse_datetime, DATETIME_FORMAT
from ai_api_client_sdk.models.execution_schedule import ExecutionSchedule
from ai_api_client_sdk.models.status import ScheduleStatus
from ai_api_client_sdk.resource_clients.execution_schedule_client import ExecutionScheduleClient
from .resource_client_test_base import ResourceClientTestBase


class TestExecutionScheduleClient(ResourceClientTestBase):
    def setUp(self):
        super().setUp()
        self.client = ExecutionScheduleClient(self.rest_client_mock)

    @staticmethod
    def create_execution_schedule_dict():
        return {
            "id": str(uuid.uuid4()),
            "cron": "0 0 0 1 *",
            "name": "test schedule",
            "configuration_id": str(uuid.uuid4()),
            "status": ScheduleStatus.ACTIVE.value,
            "start": "2023-04-05T22:17:25Z",
            "end": "2023-04-05T22:17:25Z",
            "created_at": "2023-03-29T12:58:05Z",
            "modified_at": "2023-03-30T12:58:05Z"
        }

    def assert_execution_schedule(self, es_dict: dict, es: ExecutionSchedule):
        es_dict['status'] = ScheduleStatus(es_dict['status'])
        es_dict['created_at'] = parse_datetime(es_dict['created_at'])
        es_dict['modified_at'] = parse_datetime(es_dict['modified_at'])
        es_dict['start'] = parse_datetime(es_dict['start'])
        es_dict['end'] = parse_datetime(es_dict['end'])
        self.assert_object(es_dict, es)

    def test_get_execution_schedule(self):
        es_dict = self.create_execution_schedule_dict()
        self.rest_client_mock.get.return_value = copy.deepcopy(es_dict)
        exec_schedule = self.client.get(execution_schedule_id=es_dict['id'],
                                        resource_group=self.resource_group)
        self.rest_client_mock.get.assert_called_with(path=f'/executionSchedules/{es_dict["id"]}',
                                                     resource_group=self.resource_group)
        self.assert_execution_schedule(es_dict, exec_schedule)

    def test_create_execution_schedule(self):
        es_dict = self.create_execution_schedule_dict()
        response_message = 'Execution Schedule created'
        self.rest_client_mock.post.return_value = {'id': es_dict['id'], 'message': response_message}
        ecr = self.client.create(name='test schedule', cron="0 0 0 1 *", configuration_id=es_dict['configuration_id'],
                                 start=parse_datetime(es_dict['start']), resource_group=self.resource_group)
        body = {
            "name": es_dict['name'],
            "cron": es_dict['cron'],
            "configuration_id": es_dict['configuration_id'],
            "start": es_dict['start']
        }

        self.rest_client_mock.post.assert_called_with(path='/executionSchedules', body=body,
                                                      resource_group=self.resource_group)
        self.assertEqual(es_dict['id'], ecr.id)
        self.assertEqual(response_message, ecr.message)

    def test_query_execution_schedules(self):
        n = 3
        es_dicts = [self.create_execution_schedule_dict() for _ in range(n)]
        self.rest_client_mock.get.return_value = {'resources': copy.deepcopy(es_dicts), 'count': n}
        eqr = self.client.query()
        self.rest_client_mock.get.assert_called_with(path='/executionSchedules', params=None, resource_group=None)
        self.assert_object_lists(es_dicts, eqr.resources, self.assert_execution_schedule)

        params = {'configuration_id': 'test_configuration_id', 'status': ScheduleStatus.ACTIVE, 'top': 5,
                  'skip': 1}
        self.rest_client_mock.get.return_value = {'resources': [], 'count': 0}
        self.client.query(resource_group=self.resource_group, **params)
        params['status'] = params['status'].value
        self.rest_client_mock.get.assert_called_with(path='/executionSchedules', params=params,
                                                     resource_group=self.resource_group)

    def test_modify_execution_schedule(self):
        response_dict = {'id': 'test_execution_schedule_id', 'message': 'Execution Schedule modified'}
        body = {
            "cron": "1 1 1 1 *",
            "start": parse_datetime("2023-04-15T09:00:00Z"),
            "end": parse_datetime("2023-05-15T09:00:00Z"),
            "configurationId": "aa97b177-9383-4934-8543-0f91a7a0283a",
            "status": ScheduleStatus.INACTIVE
        }
        self.rest_client_mock.patch.return_value = response_dict
        br = self.client.modify(execution_schedule_id=response_dict['id'], resource_group=self.resource_group, **body)
        body['start'] = body['start'].strftime(DATETIME_FORMAT)
        body['end'] = body['end'].strftime(DATETIME_FORMAT)
        body['status'] = body['status'].value
        self.rest_client_mock.patch.assert_called_with(path=f'/executionSchedules/{response_dict["id"]}', body=body,
                                                       resource_group=self.resource_group)
        self.assertEqual(response_dict['id'], br.id)
        self.assertEqual(response_dict['message'], br.message)

    def test_delete_execution_schedule(self):
        response_dict = {'id': 'test_execution_schedule_id', 'message': 'Execution Schedule deleted'}
        self.rest_client_mock.delete.return_value = response_dict
        br = self.client.delete(execution_schedule_id=response_dict['id'], resource_group=self.resource_group)
        self.rest_client_mock.delete.assert_called_with(path=f'/executionSchedules/{response_dict["id"]}',
                                                        resource_group=self.resource_group)
        self.assertEqual(response_dict['id'], br.id)
        self.assertEqual(response_dict['message'], br.message)

    def test_count_execution_schedules(self):
        self.assert_count('/executionSchedules/$count', 7)
        self.assert_count('/executionSchedules/$count', 5, {'configuration_id': 'test_configuration_id'})
        self.assert_count('/executionSchedules/$count', 3, {'status': ScheduleStatus.INACTIVE})
        self.assert_count('/executionSchedules/$count', 0,
                          {'configuration_id': 'test_configuration_id',
                           'status': ScheduleStatus.ACTIVE})
