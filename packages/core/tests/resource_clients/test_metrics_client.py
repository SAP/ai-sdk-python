from unittest.mock import MagicMock

from ai_api_client_sdk.models.metric import Metric
from ai_api_client_sdk.models.metric_custom_info import MetricCustomInfo
from ai_api_client_sdk.models.metric_label import MetricLabel
from ai_api_client_sdk.models.metric_tag import MetricTag

from ai_core_sdk.exception import AICoreSDKException
from .resource_client_test_base import ResourceClientTestBase
from ai_core_sdk.resource_clients.metrics_client import MetricsCoreClient


class TestMetricsCoreClient(ResourceClientTestBase):
    def setUp(self):
        self.rest_client_mock = MagicMock()
        self.metrics_client = MetricsCoreClient(self.rest_client_mock)

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

    def test_modify_metrics(self):
        metrics_patch_data = self.__patch_metrics_body(execution_id='test_execution_id')
        body = {'execution_id': metrics_patch_data.get('execution_id'),
                'metrics': [Metric.from_dict(md) for md in metrics_patch_data['metrics']],
                'tags': [MetricTag.from_dict(mtd) for mtd in metrics_patch_data['tags']],
                'custom_info': [MetricCustomInfo.from_dict(mcid) for mcid in metrics_patch_data['custom_info']]}
        self.metrics_client.modify(**body, resource_group=self.resource_group)

        self.rest_client_mock.patch.assert_called_with(path='/metrics',
                                                       body=self.__patch_metrics_body(execution_id='test_execution_id'),
                                                       resource_group=self.resource_group)

    def test_log_metrics(self):
        metrics_patch_data = self.__patch_metrics_body(execution_id='test_execution_id')
        body = {
            'execution_id': metrics_patch_data.get('execution_id'),
            'metrics': [Metric.from_dict(md) for md in metrics_patch_data['metrics']],
            'artifact_name': 'test_artifact'
        }
        self.metrics_client.log_metrics(**body, resource_group=self.resource_group)
        self.rest_client_mock.patch.assert_called_with(path='/metrics',
                                                       body={
                                                            'execution_id': metrics_patch_data.get('execution_id'),
                                                            'metrics':self.__patch_metrics_body_with_artifact_label(execution_id='test_execution_id')['metrics']
                                                       },
                                                       resource_group=self.resource_group)

    def test_set_custom_info(self):
        metrics_patch_data = self.__patch_metrics_body(execution_id='test_execution_id')
        body = {
            'execution_id': metrics_patch_data.get('execution_id'),
            'custom_info': [MetricCustomInfo.from_dict(md) for md in metrics_patch_data['custom_info']],
        }
        self.metrics_client.set_custom_info(**body, resource_group=self.resource_group)

        self.rest_client_mock.patch.assert_called_with(path='/metrics',
                                                       body={
                                                            'execution_id': metrics_patch_data.get('execution_id'),
                                                            'custom_info':self.__patch_metrics_body(execution_id='test_execution_id')['custom_info']
                                                       },
                                                       resource_group=self.resource_group)

    def test_set_tags(self):
        metrics_patch_data = self.__patch_metrics_body(execution_id='test_execution_id')
        body = {
            'execution_id': metrics_patch_data.get('execution_id'),
            'tags': [MetricTag.from_dict(md) for md in metrics_patch_data['tags']],
        }
        self.metrics_client.set_tags(**body, resource_group=self.resource_group)

        self.rest_client_mock.patch.assert_called_with(path='/metrics',
                                                       body={
                                                            'execution_id': metrics_patch_data.get('execution_id'),
                                                            'tags':self.__patch_metrics_body(execution_id='test_execution_id')['tags']
                                                       },
                                                       resource_group=self.resource_group)

    def test_modify_uses_passed_execution_id_over_instance(self):
        client = MetricsCoreClient(self.rest_client_mock, execution_id="default_exec_id")

        metrics_patch_data = self.__patch_metrics_body(execution_id='method_exec_id')
        metrics = [Metric.from_dict(md) for md in metrics_patch_data['metrics']]

        client.modify(execution_id='method_exec_id', metrics=metrics, resource_group=self.resource_group)

        expected_body = {
            'execution_id': 'method_exec_id',
            'metrics': [m.to_dict() for m in metrics],
        }

        self.rest_client_mock.patch.assert_called_with(
            path='/metrics',
            body=expected_body,
            resource_group=self.resource_group,
        )

    def test_log_metrics_uses_passed_execution_id_over_instance(self):
        client = MetricsCoreClient(self.rest_client_mock, execution_id="default_exec_id")

        metrics_patch_data = self.__patch_metrics_body(execution_id='method_exec_id')
        metrics = [Metric.from_dict(md) for md in metrics_patch_data['metrics']]

        client.log_metrics(
            execution_id='method_exec_id',
            metrics=metrics,
            artifact_name='test_artifact',
            resource_group=self.resource_group,
        )

        expected_metrics = [m.to_dict() for m in metrics]

        expected_body = {
            'execution_id': 'method_exec_id',
            'metrics': expected_metrics,
        }

        self.rest_client_mock.patch.assert_called_with(
            path='/metrics',
            body=expected_body,
            resource_group=self.resource_group,
        )

    def test_set_custom_info_uses_passed_execution_id_over_instance(self):
        client = MetricsCoreClient(self.rest_client_mock, execution_id="default_exec_id")

        metrics_patch_data = self.__patch_metrics_body(execution_id='method_exec_id')
        custom_info = [MetricCustomInfo.from_dict(ci) for ci in metrics_patch_data['custom_info']]

        client.set_custom_info(
            execution_id='method_exec_id',
            custom_info=custom_info,
            resource_group=self.resource_group,
        )

        expected_body = {
            'execution_id': 'method_exec_id',
            'custom_info': [ci.__dict__ for ci in custom_info],
        }

        self.rest_client_mock.patch.assert_called_with(
            path='/metrics',
            body=expected_body,
            resource_group=self.resource_group,
        )

    def test_set_tags_uses_passed_execution_id_over_instance(self):
        client = MetricsCoreClient(self.rest_client_mock, execution_id="default_exec_id")

        metrics_patch_data = self.__patch_metrics_body(execution_id='method_exec_id')
        tags = [MetricTag.from_dict(t) for t in metrics_patch_data['tags']]

        client.set_tags(
            execution_id='method_exec_id',
            tags=tags,
            resource_group=self.resource_group,
        )

        expected_body = {
            'execution_id': 'method_exec_id',
            'tags': [t.__dict__ for t in tags],
        }

        self.rest_client_mock.patch.assert_called_with(
            path='/metrics',
            body=expected_body,
            resource_group=self.resource_group,
        )

                                                       
