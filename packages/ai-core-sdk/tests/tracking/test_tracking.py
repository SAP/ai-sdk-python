import copy
import uuid
import os

from unittest.mock import MagicMock
from unittest import mock

from ai_api_client_sdk.models.metric import Metric
from ai_api_client_sdk.models.metric_custom_info import MetricCustomInfo
from ai_api_client_sdk.models.metric_resource import MetricResource
from ai_api_client_sdk.models.metric_tag import MetricTag

from ai_core_sdk.tracking import Tracking
from ai_core_sdk.resource_clients.metrics_client import MetricsCoreClient
from ai_core_sdk.exception import AIAPIAuthenticatorException

from ..resource_clients.resource_client_test_base import ResourceClientTestBase

class TestTracking(ResourceClientTestBase):
    def setUp(self):
        n = 3
        self.rest_client_mock = MagicMock()
        self.metric_resource_dicts = [self.create_metric_resource_dict() for _ in range(n)]
        self.rest_client_mock.get.return_value = {'resources': copy.deepcopy(self.metric_resource_dicts), 'count': n}
        token_creator = MagicMock()
        self.tracking = Tracking('http://test_url', token_creator=token_creator)
        self.tracking.metrics_core_client = MetricsCoreClient(self.rest_client_mock)

    @staticmethod
    def create_metric_resource_dict():
        return {
            "execution_id": str(uuid.uuid4()),
            "metrics": [
                {
                    "name": "Error Rate",
                    "value": 0.98,
                    "timestamp": "2021-03-29T12:58:05Z",
                    "step": 2,
                    "labels": [
                        {
                            "name": "group",
                            "value": "tree-82"
                        }
                    ]
                }
            ],
            "tags": [
                {
                    "name": "Artifact Group",
                    "value": "RFC-1"
                }
            ],
            "custom_info": [
                {
                    "name": "Confusion Matrix",
                    "value": "test_confusion_matrix"
                }
            ]
        }

    @staticmethod
    def __patch_metrics_body(execution_id):
        patch_mb = {
            "execution_id": execution_id,
            "metrics": [
                {
                    "name": "Test Error Rate",
                    "value": 0.98,
                    "timestamp": "2021-06-10T06:22:19Z",
                    "step": 2,
                    "labels": [
                        {
                            "name": "group",
                            "value": "tree-82"
                        }
                    ]
                }
            ],
            "tags": [
                {
                    "name": "Test Artifact Group",
                    "value": "RFC-1"
                }
            ],
            "custom_info": [
                {
                    "name": "Test Confusion Matrix",
                    "value": "[{'Predicted': 'False',  'Actual': 'False','value': 34}]"
                }
            ]
        }
        return patch_mb

    @staticmethod
    def __patch_metrics_body_with_artifact_label(execution_id):
        patch_mb = {
            "execution_id": execution_id,
            "metrics": [
                {
                    "name": "Test Error Rate",
                    "value": 0.98,
                    "timestamp": "2021-06-10T06:22:19Z",
                    "step": 2,
                    "labels": [
                        {
                            "name": "group",
                            "value": "tree-82"
                        }, {
                            "name": "metrics.ai.sap.com/Artifact.name",
                            "value": "test_artifact"
                        }
                    ]
                }
            ],
            "tags": [
                {
                    "name": "Test Artifact Group",
                    "value": "RFC-1"
                }
            ],
            "custom_info": [
                {
                    "name": "Test Confusion Matrix",
                    "value": "[{'Predicted': 'False',  'Actual': 'False','value': 34}]"
                }
            ]
        }
        return patch_mb

    def test_tracking_modify_metrics(self):
        metrics_patch_data = self.__patch_metrics_body(execution_id='test_execution_id')
        body = {'execution_id': metrics_patch_data.get('execution_id'),
                'metrics': [Metric.from_dict(md) for md in metrics_patch_data['metrics']],
                'tags': [MetricTag.from_dict(mtd) for mtd in metrics_patch_data['tags']],
                'custom_info': [MetricCustomInfo.from_dict(mcid) for mcid in metrics_patch_data['custom_info']]}
        self.tracking.modify(**body, resource_group=self.resource_group)

        self.rest_client_mock.patch.assert_called_with(path='/metrics',
                                                       body=self.__patch_metrics_body(execution_id='test_execution_id'),
                                                       resource_group=self.resource_group)

    def test_tracking_log_metrics(self):
        metrics_patch_data = self.__patch_metrics_body(execution_id='test_execution_id')
        body = {
            'execution_id': metrics_patch_data.get('execution_id'),
            'metrics': [Metric.from_dict(md) for md in metrics_patch_data['metrics']],
            'artifact_name': 'test_artifact'
        }
        self.tracking.log_metrics(**body, resource_group=self.resource_group)
        self.rest_client_mock.patch.assert_called_with(path='/metrics',
                                                       body={
                                                            'execution_id': metrics_patch_data.get('execution_id'),
                                                            'metrics':self.__patch_metrics_body_with_artifact_label(execution_id='test_execution_id')['metrics']
                                                       },
                                                       resource_group=self.resource_group)

    def test_tracking_set_custom_info(self):
        metrics_patch_data = self.__patch_metrics_body(execution_id='test_execution_id')
        body = {
            'execution_id': metrics_patch_data.get('execution_id'),
            'custom_info': [MetricCustomInfo.from_dict(md) for md in metrics_patch_data['custom_info']],
        }
        self.tracking.set_custom_info(**body, resource_group=self.resource_group)

        self.rest_client_mock.patch.assert_called_with(path='/metrics',
                                                       body={
                                                            'execution_id': metrics_patch_data.get('execution_id'),
                                                            'custom_info':self.__patch_metrics_body(execution_id='test_execution_id')['custom_info']
                                                       },
                                                       resource_group=self.resource_group)

    def test_tracking_set_tags(self):
        metrics_patch_data = self.__patch_metrics_body(execution_id='test_execution_id')
        body = {
            'execution_id': metrics_patch_data.get('execution_id'),
            'tags': [MetricTag.from_dict(md) for md in metrics_patch_data['tags']],
        }
        self.tracking.set_tags(**body, resource_group=self.resource_group)

        self.rest_client_mock.patch.assert_called_with(path='/metrics',
                                                       body={
                                                            'execution_id': metrics_patch_data.get('execution_id'),
                                                            'tags':self.__patch_metrics_body(execution_id='test_execution_id')['tags']
                                                       },
                                                       resource_group=self.resource_group)

    def assert_metric_resources(self, mr_dict: dict, mr: MetricResource):
        if 'metrics' in mr_dict: 
            mr_dict['metrics'] = [Metric.from_dict(md) for md in mr_dict['metrics']]
        if 'tags' in mr_dict: 
            mr_dict['tags'] = [MetricTag.from_dict(mtd) for mtd in mr_dict['tags']]
        if 'custom_info' in mr_dict:
            mr_dict['custom_info'] = [MetricCustomInfo.from_dict(mcid) for mcid in mr_dict['custom_info']]
    
    def test_tracking_query_metrics(self):
        params = {'$filter': 'test_filter', 'execution_ids': ['test_exec_id']}

        mqr = self.tracking.query(filter=params['$filter'], execution_ids=params['execution_ids'],
                            resource_group=self.resource_group)
        params['execution_ids'] = ','.join(params['execution_ids'])
        self.rest_client_mock.get.assert_called_with(path='/metrics', params=params, resource_group=self.resource_group)
        self.assert_object_lists(self.metric_resource_dicts, mqr.resources, self.assert_metric_resources,
                                 sort_key='execution_id')

    def test_tracking_query_metrics_with_select(self):
        select = 'metrics,tags'
        select_list = select.split(',')
        params = {'$filter': 'test_filter', 'execution_ids': ['test_exec_id'], '$select': select}

        mqr = self.tracking.query(filter=params['$filter'], execution_ids=params['execution_ids'], select=select_list,
                            resource_group=self.resource_group)
        params['execution_ids'] = ','.join(params['execution_ids'])
        response_with_metrics_tags = []
        for execution_data in self.metric_resource_dicts:
            new_execution_data = {}
            new_execution_data['execution_id'] = execution_data['execution_id']
            for select in select_list:
                new_execution_data[select] = execution_data[select]
            response_with_metrics_tags.append(new_execution_data)
        self.rest_client_mock.get.assert_called_with(path='/metrics', params=params, resource_group=self.resource_group)
        self.assert_object_lists(response_with_metrics_tags, mqr.resources, self.assert_metric_resources,
                                 sort_key='execution_id')

    def test_tracking_query_with_only_execution_ids(self):
        params = {'execution_ids': ['test_exec_id']}
        mqr = self.tracking.query(execution_ids=params['execution_ids'], resource_group=self.resource_group)
        params['execution_ids'] = ','.join(params['execution_ids'])
        self.rest_client_mock.get.assert_called_with(path='/metrics', params=params, resource_group=self.resource_group)
        self.assert_object_lists(self.metric_resource_dicts, mqr.resources, self.assert_metric_resources,
                                 sort_key='execution_id')

    def test_tracking_query_metrics_with_no_parameters(self):
        mqr = self.tracking.query(resource_group=self.resource_group)
        self.rest_client_mock.get.assert_called_with(path='/metrics', params=None, resource_group=self.resource_group)
        self.assert_object_lists(self.metric_resource_dicts, mqr.resources, self.assert_metric_resources,
                                 sort_key='execution_id')

    def test_tracking_delete_metrics(self):
        execution_id = 'test_exec_id'
        self.tracking.delete(execution_id=execution_id, resource_group=self.resource_group)
        params = {'execution_id': execution_id}
        self.rest_client_mock.delete.assert_called_with(path='/metrics', params=params,
                                                        resource_group=self.resource_group)

    def test_tracking_query_metrics_local(self):
        params = {'$filter': 'test_filter', 'execution_ids': ['test_exec_id']}
        tracking_local = Tracking()
        mqr = tracking_local.query(filter=params['$filter'], execution_ids=params['execution_ids'],
                            resource_group=self.resource_group)
        params['execution_ids'] = ','.join(params['execution_ids'])
        self.rest_client_mock.get.assert_not_called()

    def test_tracking_query_metrics_within_aicore(self):
        params = {'$filter': 'test_filter', 'execution_ids': ['test_exec_id']}
        response_payload = {
            'resources': copy.deepcopy(self.metric_resource_dicts),
            'count': len(self.metric_resource_dicts)
        }
        with mock.patch.dict(
            os.environ,
            {
                'AICORE_EXECUTION_ID': 'test_execution_id',
                'AICORE_TRACKING_ENDPOINT': 'https://mock/tracking',
                'AI-MAIN-TENANT': 'test_main_tenant',
                'AI-RESOURCE-GROUP': 'test_resource_group',
            },
            clear=False,
        ):
            with mock.patch(
                "ai_core_sdk.resource_clients.internal_rest_client.RestClient._handle_request",
                return_value=response_payload,
            ) as handle_request_mock:
                tracking_within_aicore = Tracking()
                mqr = tracking_within_aicore.query(filter=params['$filter'], execution_ids=params['execution_ids'])
                expected_params = params.copy()
                expected_params['execution_ids'] = ','.join(expected_params['execution_ids'])
                handle_request_mock.assert_called_once()
                call_kwargs = handle_request_mock.call_args.kwargs
                self.assertEqual(call_kwargs['params'], expected_params)
                forwarded_headers = call_kwargs['headers']
                self.assertEqual(forwarded_headers['AI-MAIN-TENANT'], 'test_main_tenant')
                self.assertEqual(forwarded_headers['AI-RESOURCE-GROUP'], 'test_resource_group')
                rest_client = tracking_within_aicore.metrics_core_client.rest_client
                self.assertEqual(rest_client.tenant, 'test_main_tenant')
                self.assertEqual(rest_client.resource_group, 'test_resource_group')
        self.assert_object_lists(self.metric_resource_dicts, mqr.resources, self.assert_metric_resources,
                                 sort_key='execution_id')

    def test_tracking_authenticator_exception(self):
        with self.assertRaises(AIAPIAuthenticatorException):
            self.tracking = Tracking('http://test_url')