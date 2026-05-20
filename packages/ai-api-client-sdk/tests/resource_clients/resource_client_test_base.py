from typing import Any, Callable, Dict, List, Union
from unittest import TestCase
from unittest.mock import MagicMock

from ai_api_client_sdk.helpers.datetime_parser import parse_datetime
from ai_api_client_sdk.models.enactment import Enactment
from ai_api_client_sdk.models.status import Status
from ai_api_client_sdk.models.target_status import TargetStatus


class ResourceClientTestBase(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.resource_group = 'test_resource_group'

    def setUp(self):
        super().setUp()
        self.rest_client_mock = MagicMock()
        self.client = None

    def assert_object(self, d: Dict[str, Any], o: object):
        for k in d.keys():
            self.assertEqual(d[k], getattr(o, k))

    def assert_enactment(self, e_dict: dict, e: Enactment):
        e_dict['created_at'] = parse_datetime(e_dict['created_at'])
        e_dict['modified_at'] = parse_datetime(e_dict['modified_at'])
        e_dict['status'] = Status(e_dict['status'])
        e_dict['target_status'] = TargetStatus(e_dict['target_status'])
        e_dict['submission_time'] = parse_datetime(e_dict['submission_time'])
        e_dict['start_time'] = parse_datetime(e_dict['start_time'])
        e_dict['completion_time'] = parse_datetime(e_dict['completion_time'])
        self.assert_object(e_dict, e)

    def assert_object_lists(self, dict_list: List[Dict[str, Any]], object_list: list,
                            assert_object_function: Callable = None, sort_key: str = 'id'):
        if not assert_object_function:
            assert_object_function = self.assert_object
        self.assertEqual(len(dict_list), len(object_list))
        dict_list = sorted(dict_list, key=lambda ad: ad[sort_key])
        object_list = sorted(object_list, key=lambda a: getattr(a, sort_key))
        for i in range(len(object_list)):
            assert_object_function(dict_list[i], object_list[i])

    def assert_count(self, path: str, count: int, params: Union[Dict[str, Any], None] = None):
        params = params
        self.rest_client_mock.get.return_value = count
        if params:
            res_count = self.client.count(resource_group=self.resource_group, **params)
            if 'executable_ids' in params:
                params['executable_ids'] = ','.join(params['executable_ids'])
            if 'status' in params:
                params['status'] = params['status'].value
            if 'kind' in params:
                params['kind'] = params['kind'].value
            if 'search' in params:
                params['$search'] = params['search']
                del params['search']
            if 'expand' in params:
                params['$expand'] = params['expand']
                del params['expand']
        else:
            res_count = self.client.count(resource_group=self.resource_group)

        self.rest_client_mock.get.assert_called_with(path=path, params=params,
                                                     resource_group=self.resource_group)
        self.assertEqual(res_count, count)
