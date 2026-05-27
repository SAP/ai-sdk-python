import copy
import uuid
from datetime import datetime
from unittest.mock import MagicMock

from ai_api_client_sdk.helpers.datetime_parser import DATETIME_FORMAT
from ai_api_client_sdk.models.metric import Metric
from ai_api_client_sdk.models.metric_custom_info import MetricCustomInfo
from ai_api_client_sdk.models.metric_label import MetricLabel
from ai_api_client_sdk.models.metric_resource import MetricResource
from ai_api_client_sdk.models.metric_tag import MetricTag
from ai_api_client_sdk.resource_clients.metrics_client import MetricsClient
from .resource_client_test_base import ResourceClientTestBase


class TestMetricsClient(ResourceClientTestBase):
    def setUp(self):
        n = 3
        self.metric_resource_dicts = [self.create_metric_resource_dict() for _ in range(n)]
        self.rest_client_mock = MagicMock()
        self.rest_client_mock.get.return_value = {'resources': copy.deepcopy(self.metric_resource_dicts), 'count': n}
        self.mc = MetricsClient(self.rest_client_mock)

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

    def assert_metric_resources(self, mr_dict: dict, mr: MetricResource):
        if 'metrics' in mr_dict: 
            mr_dict['metrics'] = [Metric.from_dict(md) for md in mr_dict['metrics']]
        if 'tags' in mr_dict: 
            mr_dict['tags'] = [MetricTag.from_dict(mtd) for mtd in mr_dict['tags']]
        if 'custom_info' in mr_dict:
            mr_dict['custom_info'] = [MetricCustomInfo.from_dict(mcid) for mcid in mr_dict['custom_info']]

    def test_query_metrics(self):
        params = {'$filter': 'test_filter', 'execution_ids': ['test_exec_id']}

        mqr = self.mc.query(filter=params['$filter'], execution_ids=params['execution_ids'],
                            resource_group=self.resource_group)
        params['execution_ids'] = ','.join(params['execution_ids'])
        self.rest_client_mock.get.assert_called_with(path='/metrics', params=params, resource_group=self.resource_group)
        self.assert_object_lists(self.metric_resource_dicts, mqr.resources, self.assert_metric_resources,
                                 sort_key='execution_id')
        self.assertIn("Metric execution id: ", mqr.resources[0].__str__())
        self.assertIn(self.metric_resource_dicts[0]['execution_id'], mqr.resources[0].__str__())
        self.assertIn("Metrics: ", mqr.resources[0].__str__())
        self.assertIn(self.metric_resource_dicts[0]['metrics'][0].name, mqr.resources[0].__str__())
        self.assertIn("Metric tag name: ", mqr.resources[0].tags[0].__str__())
        self.assertIn(self.metric_resource_dicts[0]['tags'][0].name, mqr.resources[0].tags[0].__str__())
        self.assertIn("Metric tag value: ", mqr.resources[0].tags[0].__str__())
        self.assertIn(self.metric_resource_dicts[0]['tags'][0].value, mqr.resources[0].tags[0].__str__())

    def test_query_metrics_with_select(self):
        select = 'metrics,tags'
        select_list = select.split(',')
        params = {'$filter': 'test_filter', 'execution_ids': ['test_exec_id'], '$select': select}

        mqr = self.mc.query(filter=params['$filter'], execution_ids=params['execution_ids'], select=select_list,
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

    def test_query_with_only_execution_ids(self):
        params = {'execution_ids': ['test_exec_id']}
        mqr = self.mc.query(execution_ids=params['execution_ids'], resource_group=self.resource_group)
        params['execution_ids'] = ','.join(params['execution_ids'])
        self.rest_client_mock.get.assert_called_with(path='/metrics', params=params, resource_group=self.resource_group)
        self.assert_object_lists(self.metric_resource_dicts, mqr.resources, self.assert_metric_resources,
                                 sort_key='execution_id')

    def test_query_metrics_with_no_parameters(self):
        mqr = self.mc.query(resource_group=self.resource_group)
        self.rest_client_mock.get.assert_called_with(path='/metrics', params=None, resource_group=self.resource_group)
        self.assert_object_lists(self.metric_resource_dicts, mqr.resources, self.assert_metric_resources,
                                 sort_key='execution_id')

    def test_delete_metrics(self):
        execution_id = 'test_exec_id'
        self.mc.delete(execution_id=execution_id, resource_group=self.resource_group)
        params = {'execution_id': execution_id}
        self.rest_client_mock.delete.assert_called_with(path='/metrics', params=params,
                                                        resource_group=self.resource_group)

    def test_metric_to_dict(self):
        metric = Metric(name='test_metric_name', value=0.0, timestamp=datetime.utcnow(), step=1,
                        labels=[MetricLabel(name='test_label_name', value='test_label_value')])
        metric_dict = metric.to_dict()
        self.assertEqual(metric.name, metric_dict['name'])
        self.assertEqual(metric.value, metric_dict['value'])
        self.assertEqual(metric.step, metric_dict['step'])
        self.assertTrue(isinstance(metric.timestamp, datetime))
        self.assertEqual(metric.timestamp.strftime(DATETIME_FORMAT), metric_dict['timestamp'])
        self.assertEqual(metric.labels[0].to_dict(), metric_dict['labels'][0])
        self.assertIn("Metric name", metric.__str__())
        self.assertIn(str(metric.name), metric.__str__())
        self.assertIn("Metric value", metric.__str__())
        self.assertIn(str(metric.value), metric.__str__())

    def test_metric_default_values(self):
        metric = Metric(name='test_name', value=0.0, timestamp=datetime.utcnow())
        self.assertEqual(0, metric.step)
        self.assertEqual([], metric.labels)

        test_step = 1
        test_labels = [MetricLabel(name='test_label_name', value='test_label_value')]
        metric = Metric(name='test_name', value=0.0, timestamp=datetime.utcnow(), step=test_step,
                        labels=test_labels)
        self.assertEqual(test_step, metric.step)
        self.assertEqual(test_labels, metric.labels)

