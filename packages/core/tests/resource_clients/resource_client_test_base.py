from typing import Any, Callable, Dict, List, Union
from unittest import TestCase
from unittest.mock import MagicMock


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

    def assert_object_lists(self, dict_list: List[Dict[str, Any]], object_list: list,
                            assert_object_function: Callable = None, sort_key: str = 'id'):
        if not assert_object_function:
            assert_object_function = self.assert_object
        self.assertEqual(len(dict_list), len(object_list))
        dict_list = sorted(dict_list, key=lambda ad: ad[sort_key])
        object_list = sorted(object_list, key=lambda a: getattr(a, sort_key))
        for i in range(len(object_list)):
            assert_object_function(dict_list[i], object_list[i])

    def assert_all_attributes_none(self, o: object):
        for k, v in o.__dict__.items():
            self.assertIsNone(v)
