import os
import json
import tempfile
import unittest
from unittest import TestCase
from unittest.mock import MagicMock, patch
from ai_core_sdk.ai_core_v2_client import AICoreV2Client
from ai_core_sdk.helpers.constants import (AI_CORE_PREFIX, HOME_PATH_ENV_VAR, VCAP_SERVICES_ENV_VAR,
                                           VCAP_AICORE_SERVICE_NAME)
from ai_core_sdk.exception import AIAPIAuthenticatorException
from ai_core_sdk.resource_clients.internal_rest_client import InternalRestClient
from .test_credentials import VCAP_SERVICE_X509_DICT, VCAP_SERVICE_X509_ENV_VALUE

# unit tests for AI Core V2 Client

params = ('base_url', 'auth_url', 'resource_group', 'client_id', 'client_secret')


class TestAICoreV2Client(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.base_url = 'test_base_url/v2'
        cls.auth_url = 'test_auth_url/oauth/token'
        cls.client_id = 'test_client_id'
        cls.client_secret = 'test_client_secret'
        cls.cert_str = 'test_cert_str'
        cls.key_str = 'test_key_str'
        cls.cert_file_path = 'test_cert_file_path'
        cls.key_file_path = 'test_key_file_path'

    def test_no_secret_no_cert_raises_exception(self):
        with self.assertRaises(AIAPIAuthenticatorException) as cm:
            c = AICoreV2Client(base_url=self.base_url, auth_url=self.auth_url)
        self.assertTrue('client_id' in cm.exception.error_message)

    @patch('ai_core_sdk.ai_core_v2_client.AIAPIV2Client')
    def test_happy_path_client_secret(self, ai_api_v2_client_mock):
        ai_api_v2_client_mock._create_token_creator_if_does_not_exist = MagicMock()
        c = AICoreV2Client(base_url=self.base_url, auth_url=self.auth_url, client_id=self.client_id,
                           client_secret=self.client_secret)
        ai_api_v2_client_mock._create_token_creator_if_does_not_exist.assert_called_once_with(
            token_creator=None, auth_url=self.auth_url, client_id=self.client_id, client_secret=self.client_secret,
            cert_str=None, key_str=None, cert_file_path=None, key_file_path=None)
        self.assertIsNotNone(c.rest_client)

    @patch('ai_core_sdk.ai_core_v2_client.AIAPIV2Client')
    def test_happy_path_x509_file_path(self, ai_api_v2_client_mock):
        ai_api_v2_client_mock._create_token_creator_if_does_not_exist = MagicMock()
        c = AICoreV2Client(base_url=self.base_url, auth_url=self.auth_url, client_id=self.client_id,
                           cert_file_path=self.cert_file_path, key_file_path=self.key_file_path)
        ai_api_v2_client_mock._create_token_creator_if_does_not_exist.assert_called_once_with(
            token_creator=None, auth_url=self.auth_url, client_id=self.client_id, client_secret=None, cert_str=None,
            key_str=None, cert_file_path=self.cert_file_path, key_file_path=self.key_file_path)
        self.assertIsNotNone(c.rest_client)

    @patch('ai_core_sdk.ai_core_v2_client.AIAPIV2Client')
    def test_happy_path_x509_str(self, ai_api_v2_client_mock):
        ai_api_v2_client_mock._create_token_creator_if_does_not_exist = MagicMock()
        c = AICoreV2Client(base_url=self.base_url, auth_url=self.auth_url, client_id=self.client_id,
                           cert_str=self.cert_str, key_str=self.key_str)
        ai_api_v2_client_mock._create_token_creator_if_does_not_exist.assert_called_once_with(
            token_creator=None, auth_url=self.auth_url, client_id=self.client_id, client_secret=None,
            cert_str=self.cert_str, key_str=self.key_str, cert_file_path=None, key_file_path=None)
        self.assertIsNotNone(c.rest_client)

    @property
    def full_params(self):
        full_params = dict(
            base_url = 'https://ai-api.com/v2',
            auth_url = 'https://auth.com/oauth/token',
            client_id = 'client_id',
            client_secret = 'client_secret',
            resource_group = 'test_resource_group',
            read_timeout = 1,
            connect_timeout = 2,
            num_request_retries = 3,
        )
        return full_params

    @property
    def full_params_no_suffix(self):
        params_with_suffix = self.full_params
        params_with_suffix['base_url'] = 'https://ai-api.com/'
        params_with_suffix['auth_url'] = 'https://auth.com/'
        return params_with_suffix

    def test_regular_rest_client_used_outside_aicore(self):
        client = AICoreV2Client(**self.full_params)
        self.assertNotIsInstance(client.metrics.rest_client, InternalRestClient)

    def test_client_type_header_set_correctly(self):
        test_client_type = "Test Client Type"
        test_params = self.full_params.copy()
        test_params['client_type'] = test_client_type
        client = AICoreV2Client(**test_params)
        client_headers = client.rest_client.headers
        self.assertEqual(client_headers['AI-Client-Type'], test_client_type)

    def test_client_type_header_defaults_correctly(self):
        test_params = self.full_params.copy()
        test_params.pop('client_type', None)
        client = AICoreV2Client(**test_params)
        client_headers = client.rest_client.headers
        self.assertEqual(client_headers['AI-Client-Type'], "AI Core Python SDK")

    @patch.dict(
        os.environ,
        {
            "AICORE_EXECUTION_ID": "test-execution-id",
            "AICORE_TRACKING_ENDPOINT": "test-tracking-endpoint",
            "AI-MAIN-TENANT": "test-main-tenant",
            "AI-RESOURCE-GROUP": "test_resource_group",
        },
    )
    def test_internal_rest_client_used_within_aicore(self):
        client = AICoreV2Client(**self.full_params)
        self.assertEqual(client.rest_client.headers.get(client.rest_client.client_type_header), "AI Core Python SDK")

        self.assertIsInstance(client.metrics.rest_client, InternalRestClient)

        # check if attributes adjusted by InternalRestClient are properly set
        self.assertEqual(
            client.metrics.rest_client.base_url, "test-tracking-endpoint/api/v1"
        )
        self.assertEqual(
            client.metrics.rest_client.resource_group_header, "AI-Resource-Group"
        )
        self.assertEqual(client.metrics.rest_client.get_token(), "")

        # check if other parameters are properly set
        partial_params = {
            x: self.full_params[x]
            for x in self.full_params
            if x
            not in {
                "base_url",
                "resource_group",
                "token_creator",
                # also excluding parameters transformed further
                "auth_url",
                "client_id",
                "client_secret",
            }
        }
        for param_key in partial_params:
            self.assertEqual(
                getattr(client.metrics.rest_client, param_key),
                partial_params[param_key],
            )

    def get_x509_file_path_dict(self):
        return {
            f'{AI_CORE_PREFIX}_BASE_URL': self.base_url,
            f'{AI_CORE_PREFIX}_AUTH_URL': self.auth_url,
            f'{AI_CORE_PREFIX}_CLIENT_ID': self.client_id,
            f'{AI_CORE_PREFIX}_CERT_FILE_PATH': self.cert_file_path,
            f'{AI_CORE_PREFIX}_KEY_FILE_PATH': self.key_file_path
        }

    def get_x509_str_dict(self):
        return {
            f'{AI_CORE_PREFIX}_BASE_URL': self.base_url,
            f'{AI_CORE_PREFIX}_AUTH_URL': self.auth_url,
            f'{AI_CORE_PREFIX}_CLIENT_ID': self.client_id,
            f'{AI_CORE_PREFIX}_CERT_STR': self.cert_str,
            f'{AI_CORE_PREFIX}_KEY_STR': self.key_str
        }

    def test_x509_str_from_env(self):
        init_mock = MagicMock(return_value=None)
        aicv2c_init = AICoreV2Client.__init__
        AICoreV2Client.__init__ = init_mock
        mock_env = self.get_x509_str_dict()

        with patch.dict(os.environ, mock_env):
            AICoreV2Client.from_env()
            AICoreV2Client.__init__.assert_called_once_with(base_url=self.base_url, auth_url=self.auth_url,
                                                            client_id=self.client_id,
                                                            cert_str=self.cert_str,
                                                            key_str=self.key_str)

        AICoreV2Client.__init__ = aicv2c_init

    def test_x509_file_path_from_config(self):
        init_mock = MagicMock(return_value=None)
        aicv2c_init = AICoreV2Client.__init__
        AICoreV2Client.__init__ = init_mock

        config = self.get_x509_file_path_dict()
        for k, v in config.items():
            config[k] = f'cfg_{v}'

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {HOME_PATH_ENV_VAR: temp_dir}):
                config_file_path = os.path.join(temp_dir, 'config.json')
                with open(config_file_path, 'w') as f:
                    json.dump(config, f)
                AICoreV2Client.from_env()
                AICoreV2Client.__init__.assert_called_once_with(base_url=f'cfg_{self.base_url}',
                                                                auth_url=f'cfg_{self.auth_url}',
                                                                client_id=f'cfg_{self.client_id}',
                                                                cert_file_path=f'cfg_{self.cert_file_path}',
                                                                key_file_path=f'cfg_{self.key_file_path}')

        AICoreV2Client.__init__ = aicv2c_init

    @patch.dict(os.environ, {VCAP_SERVICES_ENV_VAR: VCAP_SERVICE_X509_ENV_VALUE})
    def test_x509_from_vcap(self):
        vcap_dict_credentials = VCAP_SERVICE_X509_DICT[VCAP_AICORE_SERVICE_NAME][0]['credentials']
        init_mock = MagicMock(return_value=None)
        aicv2c_init = AICoreV2Client.__init__
        AICoreV2Client.__init__ = init_mock

        AICoreV2Client.from_env()

        AICoreV2Client.__init__.assert_called_once_with(
            base_url=f'{vcap_dict_credentials["serviceurls"]["AI_API_URL"]}/v2',
            auth_url=f'{vcap_dict_credentials["certurl"]}/oauth/token',
            client_id=vcap_dict_credentials['clientid'],
            cert_str=vcap_dict_credentials['certificate'],
            key_str=vcap_dict_credentials['key'])

        AICoreV2Client.__init__ = aicv2c_init

    @patch.dict(os.environ, {"AICORE_HOME": "XXX"}, clear=False)
    def test_from_env(self):
        """Test from_env with single-source credential resolution.

        The credential resolution priority is:
        - Once a source (kwargs, env, config, VCAP) has any credential, ALL credentials come from that source
        - Resource group is resolved separately with first source wins logic
        """
        init_mock = MagicMock(return_value=None)
        aicv2c_init = AICoreV2Client.__init__

        try:
            AICoreV2Client.__init__ = init_mock

            # Test 1: All parameters provided via kwargs - should use kwargs as source
            AICoreV2Client.from_env(**self.full_params)
            AICoreV2Client.__init__.assert_called_once_with(**self.full_params)
            init_mock.reset_mock()

            # Test 2: Credentials from env variables (no kwargs credentials)
            env_credentials = {
                'AICORE_BASE_URL': 'https://env-api.com/v2',
                'AICORE_AUTH_URL': 'https://env-auth.com/oauth/token',
                'AICORE_CLIENT_ID': 'env_client_id',
                'AICORE_CLIENT_SECRET': 'env_client_secret',
            }
            with patch.dict(os.environ, env_credentials, clear=False):
                AICoreV2Client.from_env()
                AICoreV2Client.__init__.assert_called_once_with(
                    base_url='https://env-api.com/v2',
                    auth_url='https://env-auth.com/oauth/token',
                    client_id='env_client_id',
                    client_secret='env_client_secret',
                )
            init_mock.reset_mock()

            # Test 3: Credentials from config file
            with tempfile.TemporaryDirectory() as temp_dir:
                config_credentials = {
                    'AICORE_BASE_URL': 'https://config-api.com/v2',
                    'AICORE_AUTH_URL': 'https://config-auth.com/oauth/token',
                    'AICORE_CLIENT_ID': 'config_client_id',
                    'AICORE_CLIENT_SECRET': 'config_client_secret',
                }
                config_file_path = os.path.join(temp_dir, 'config.json')
                with open(config_file_path, 'w') as f:
                    json.dump(config_credentials, f)

                with patch.dict(os.environ, {'AICORE_HOME': temp_dir}, clear=False):
                    AICoreV2Client.from_env()
                    AICoreV2Client.__init__.assert_called_once_with(
                        base_url='https://config-api.com/v2',
                        auth_url='https://config-auth.com/oauth/token',
                        client_id='config_client_id',
                        client_secret='config_client_secret',
                    )
                init_mock.reset_mock()

            # Test 4: Named profile config file
            with tempfile.TemporaryDirectory() as temp_dir:
                profile_name = 'test'
                profile_credentials = {
                    'AICORE_BASE_URL': 'https://profile-api.com/v2',
                    'AICORE_AUTH_URL': 'https://profile-auth.com/oauth/token',
                    'AICORE_CLIENT_ID': 'profile_client_id',
                    'AICORE_CLIENT_SECRET': 'profile_client_secret',
                }
                config_file_path = os.path.join(temp_dir, f'config_{profile_name}.json')
                with open(config_file_path, 'w') as f:
                    json.dump(profile_credentials, f)

                with patch.dict(os.environ, {'AICORE_HOME': temp_dir}, clear=False):
                    AICoreV2Client.from_env(profile_name=profile_name)
                    AICoreV2Client.__init__.assert_called_once_with(
                        base_url='https://profile-api.com/v2',
                        auth_url='https://profile-auth.com/oauth/token',
                        client_id='profile_client_id',
                        client_secret='profile_client_secret',
                    )
                init_mock.reset_mock()

            # Test 5: Resource group override - resource_group from kwargs overrides config
            with tempfile.TemporaryDirectory() as temp_dir:
                config_with_rg = {
                    'AICORE_BASE_URL': 'https://config-api.com/v2',
                    'AICORE_AUTH_URL': 'https://config-auth.com/oauth/token',
                    'AICORE_CLIENT_ID': 'config_client_id',
                    'AICORE_CLIENT_SECRET': 'config_client_secret',
                    'AICORE_RESOURCE_GROUP': 'config_rg',
                }
                config_file_path = os.path.join(temp_dir, 'config.json')
                with open(config_file_path, 'w') as f:
                    json.dump(config_with_rg, f)

                with patch.dict(os.environ, {'AICORE_HOME': temp_dir}, clear=False):
                    # Pass resource_group via kwargs - should override config
                    AICoreV2Client.from_env(resource_group='kwargs_rg')
                    AICoreV2Client.__init__.assert_called_once_with(
                        base_url='https://config-api.com/v2',
                        auth_url='https://config-auth.com/oauth/token',
                        client_id='config_client_id',
                        client_secret='config_client_secret',
                        resource_group='kwargs_rg',
                    )
                init_mock.reset_mock()
        finally:
            AICoreV2Client.__init__ = aicv2c_init


if __name__ == "__main__":
    unittest.main()
