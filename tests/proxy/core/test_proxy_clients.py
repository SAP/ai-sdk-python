import unittest

from gen_ai_hub.proxy.core.proxy_clients import (
    ProxyClients,
    get_proxy_client,
    get_proxy_version,
    proxy_version_context,
    set_proxy_version,
)
from tests.mock import MockProxyClient


class TestProxyManagement(unittest.TestCase):

    def test_proxy_version_context(self):
        """ Test the proxy_version_context context manager. """
        original_value = get_proxy_version()
        new_value = original_value + '_new'
        with proxy_version_context(new_value):
            self.assertEqual(get_proxy_version(), new_value)
        # Test restoring previous state
        self.assertEqual(get_proxy_version(), original_value)

    def test_set_proxy_version(self):
        """ Test setting the proxy version. """
        catalog = ProxyClients()
        set_proxy_version('v2', catalog=catalog)
        self.assertEqual(get_proxy_version(catalog=catalog), 'v2')

    def test_get_proxy_client(self):
        """ Test getting a proxy client. """
        proxy_clients = ProxyClients()

        @proxy_clients.register('test')
        class TestProxyClient(MockProxyClient):
            pass

        client = get_proxy_client('test', catalog=proxy_clients)
        self.assertIsInstance(client, TestProxyClient)

    def test_proxy_clients_registration(self):
        """ Test registering and retrieving a proxy client class. """
        proxy_clients = ProxyClients()
        proxy_clients.register('mock')(MockProxyClient)

        @proxy_clients.register('mock_v2')
        class DifferentProxyClient(MockProxyClient):
            pass

        self.assertIs(proxy_clients.get_proxy_cls('mock_v2'), DifferentProxyClient)

    def test_get_proxy_cls_name(self):
        """ Test retrieving the name of a registered proxy client class. """
        proxy_clients = ProxyClients()

        proxy_clients.register('mock')(MockProxyClient)

        self.assertEqual(proxy_clients.get_proxy_cls_name(MockProxyClient), 'mock')

    def test_errors(self):
        """ Test error handling in various functions. """
        proxy_clients = ProxyClients()

        with self.assertRaises(ValueError):
            set_proxy_version(123)  # Not a string

        with self.assertRaises(ValueError):
            @proxy_clients.register('test')
            class NotAProxyClient:
                pass

        with self.assertRaises(ValueError):
            proxy_clients.get_proxy_cls_name(str)


if __name__ == '__main__':
    unittest.main()
