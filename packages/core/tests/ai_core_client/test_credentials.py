from typing import Final, List
import json
import os
import pathlib
import shutil
import tempfile
import unittest
from unittest.mock import patch, MagicMock, call

from ai_core_sdk.credentials import (
    CredentialsValue,
    Service,
    VCAPEnvironment,
    fetch_credentials,
    init_conf, CORE_CREDENTIAL_VALUES,
)
from ai_core_sdk.helpers.constants import (AI_CORE_PREFIX, HOME_PATH_ENV_VAR, PROFILE_ENV_VAR, VCAP_SERVICES_ENV_VAR,
                                           VCAP_AICORE_SERVICE_NAME, CONFIG_FILE_ENV_VAR)

VCAP_SERVICE_DICT = {
    VCAP_AICORE_SERVICE_NAME: [{
        'label': VCAP_AICORE_SERVICE_NAME,
        'name': f'{VCAP_AICORE_SERVICE_NAME}-instance',
        'instance_guid': '53ad5b47-a49a-4fec-9f0b-cd921c00b828',
        'credentials': {
            'serviceurls': {
                'AI_API_URL': 'vcap-api-url'
            },
            'url': 'vcap-auth-url',
            'clientid': 'vcap-clientid',
            'clientsecret': 'vcap-clientsecret'
        }
    }]
}
VCAP_SERVICE_ENV_VALUE = json.dumps(VCAP_SERVICE_DICT, indent=4)

VCAP_SERVICE_X509_DICT = {
    VCAP_AICORE_SERVICE_NAME: [{
        'label': VCAP_AICORE_SERVICE_NAME,
        'name': f'{VCAP_AICORE_SERVICE_NAME}-instance',
        'instance_guid': '53ad5b47-a49a-4fec-9f0b-cd921c00b828',
        'credentials': {
            'serviceurls': {
                'AI_API_URL': 'vcap-api-url'
            },
            'certurl': 'vcap-cert-url',
            'clientid': 'vcap-clientid',
            'key': 'vcap-key',
            'certificate': 'vcap-certificate'
        }
    }]
}
VCAP_SERVICE_X509_ENV_VALUE = json.dumps(VCAP_SERVICE_X509_DICT, indent=4)


class TestVCAPServices(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.vcap_dict = VCAP_SERVICE_DICT[VCAP_AICORE_SERVICE_NAME][0]

    def test_vcap_services(self):
        with patch.dict(os.environ, {VCAP_SERVICES_ENV_VAR: VCAP_SERVICE_ENV_VALUE}):
            vcap_services = VCAPEnvironment.from_env()
        self.assertTrue(all(isinstance(srv, Service) for srv in vcap_services.services))
        self.assertEqual(len(vcap_services.services), 1)
        aicore_vcap_service = vcap_services[VCAP_AICORE_SERVICE_NAME]
        self.assertIsInstance(aicore_vcap_service, Service)
        self.assertEqual(aicore_vcap_service, vcap_services.get_service(VCAP_AICORE_SERVICE_NAME))
        self.assertEqual(len(vcap_services.get_service(VCAP_AICORE_SERVICE_NAME, exactly_one=False)), 1)
        self.assertEqual(aicore_vcap_service, vcap_services.get_service_by_name(self.vcap_dict['name']))
        self.assertEqual(aicore_vcap_service.label, VCAP_AICORE_SERVICE_NAME)
        self.assertEqual(aicore_vcap_service['instance_guid'], self.vcap_dict['instance_guid'])
        self.assertEqual(aicore_vcap_service['credentials.clientid'], self.vcap_dict['credentials']['clientid'])
        self.assertEqual(aicore_vcap_service['credentials', 'clientid'], self.vcap_dict['credentials']['clientid'])
        self.assertEqual(aicore_vcap_service['credentials.clientsecret'], self.vcap_dict['credentials']['clientsecret'])
        self.assertEqual(aicore_vcap_service['credentials.url'], self.vcap_dict['credentials']['url'])
        with self.assertRaises(KeyError):
            _ = aicore_vcap_service['non-existing']
        self.assertIsNone(aicore_vcap_service.get('non-existing', None))


def assert_logging_calls(mock_logger, resolved_values, default_keys, source):
    expected_calls = []
    for cred in CORE_CREDENTIAL_VALUES:
        if cred.name in resolved_values:
            expected_calls.append(
                call('Using source %s for %s', source, cred.name))
        elif cred.name in default_keys:
            expected_calls.append(call('Using source %s for %s', 'default value', cred.name))

    # Assert the calls
    mock_logger.debug.assert_has_calls(expected_calls)


class TestConfigHandling(unittest.TestCase):
    """TestCase for init_conf and from_conf functions."""

    @classmethod
    def setUpClass(cls):
        # Create a temporary directory
        cls.temp_dir = pathlib.Path(tempfile.mkdtemp())

        # Define the file name and content
        cls.file_name = 'config.json'
        cls.profile = 'test'
        cls.file_name_profile = f'config_{cls.profile}.json'
        cls.default_config = {
            f'{AI_CORE_PREFIX}_CLIENT_ID': 'default-client-id',
            f'{AI_CORE_PREFIX}_CLIENT_SECRET': 'default-client-secret',
            f'{AI_CORE_PREFIX}_BASE_URL': 'default-base-url',
            f'{AI_CORE_PREFIX}_AUTH_URL': 'default-auth-url'
        }
        cls.profile_config = {
            f'{AI_CORE_PREFIX}_CLIENT_ID': 'profile-client-id',
            f'{AI_CORE_PREFIX}_CLIENT_SECRET': 'profile-client-secret',
            f'{AI_CORE_PREFIX}_BASE_URL': 'profile-base-url'
        }

        # Create a file within this directory
        with (cls.temp_dir / cls.file_name).open('w') as file:
            json.dump(cls.default_config, file)
        with (cls.temp_dir / cls.file_name_profile).open('w') as file:
            json.dump(cls.profile_config, file)

    @classmethod
    def tearDownClass(cls):
        # Clean up the directory after all tests
        shutil.rmtree(str(cls.temp_dir))

    @patch('ai_core_sdk.credentials.logger')
    def test_init_conf(self, mock_logger):
        mock_logger.debug = MagicMock()

        # if no default config found return empty conf
        conf = init_conf()
        self.assertDictEqual(conf, {})

        # if an explicit profile is request but the config does not exist raise an error
        with self.assertRaises(FileNotFoundError):
            conf = init_conf('MOCK_LLM')

        # load default config
        with patch.dict(os.environ, {HOME_PATH_ENV_VAR: str(self.temp_dir)}):
            conf = init_conf()
            self.assertDictEqual(conf, self.default_config)
            mock_logger.debug.assert_called_with('Config file path %s', self.temp_dir / 'config.json')

        # load profile config
        with patch.dict(os.environ, {HOME_PATH_ENV_VAR: str(self.temp_dir), PROFILE_ENV_VAR: self.profile}):
            conf = init_conf()
            self.assertDictEqual(conf, self.profile_config)
            mock_logger.debug.assert_called_with('Config file path %s', self.temp_dir / self.file_name_profile)

        # load profile config with profile param
        with patch.dict(os.environ, {HOME_PATH_ENV_VAR: str(self.temp_dir)}):
            conf = init_conf(profile=self.profile)
            self.assertDictEqual(conf, self.profile_config)
            mock_logger.debug.assert_called_with('Config file path %s', self.temp_dir / self.file_name_profile)

        # load profile config via env variable
        with patch.dict(os.environ, {f'{AI_CORE_PREFIX}_PROFILE': self.profile,
                                     HOME_PATH_ENV_VAR: str(self.temp_dir)}):
            conf = init_conf()
            self.assertDictEqual(conf, self.profile_config)
            # overwrite env variable with explicit profile
            conf = init_conf(profile='default')
            self.assertDictEqual(conf, self.default_config)
            mock_logger.debug.assert_called_with('Config file path %s', self.temp_dir / 'config.json')

    @patch.dict(os.environ, {VCAP_SERVICES_ENV_VAR: VCAP_SERVICE_ENV_VALUE})
    @patch('ai_core_sdk.credentials.logger')
    def test_fetch_credentials_from_vcap_services(self, mock_logger):
        mock_logger.debug = MagicMock()

        vcap_dict_credentials = VCAP_SERVICE_DICT[VCAP_AICORE_SERVICE_NAME][0]['credentials']
        credentials = fetch_credentials()
        self.assertEqual(credentials['base_url'], f'{vcap_dict_credentials["serviceurls"]["AI_API_URL"]}/v2')
        self.assertEqual(credentials['client_secret'], vcap_dict_credentials['clientsecret'])
        self.assertEqual(credentials['client_id'], vcap_dict_credentials['clientid'])
        self.assertEqual(credentials['auth_url'], f'{vcap_dict_credentials["url"]}/oauth/token')

        mock_logger.debug.assert_any_call("Using credentials from: VCAP service")
        mock_logger.debug.assert_any_call("No resource_group found in any source")

    @patch.dict(os.environ, {VCAP_SERVICES_ENV_VAR: VCAP_SERVICE_X509_ENV_VALUE})
    @patch('ai_core_sdk.credentials.logger')
    def test_fetch_credentials_from_vcap_services_with_x509_env_var(self, mock_logger):
        mock_logger.debug = MagicMock()
        vcap_dict_credentials = VCAP_SERVICE_X509_DICT[VCAP_AICORE_SERVICE_NAME][0]['credentials']
        credentials = fetch_credentials()
        self.assertEqual(credentials['base_url'], f'{vcap_dict_credentials["serviceurls"]["AI_API_URL"]}/v2')
        self.assertEqual(credentials['client_id'], vcap_dict_credentials['clientid'])
        self.assertEqual(credentials['key_str'], vcap_dict_credentials['key'])
        self.assertEqual(credentials['cert_str'], vcap_dict_credentials['certificate'])
        self.assertEqual(credentials['auth_url'], f'{vcap_dict_credentials["certurl"]}/oauth/token')

        mock_logger.debug.assert_any_call("Using credentials from: VCAP service")
        mock_logger.debug.assert_any_call("No resource_group found in any source")

    @patch('ai_core_sdk.credentials.logger')
    def test_fetch_credentials_from_env(self, mock_logger):
        mock_logger.debug = MagicMock()

        with patch.dict(
                    os.environ,
                    {
                        f'{AI_CORE_PREFIX}_CLIENT_ID': self.default_config[f'{AI_CORE_PREFIX}_CLIENT_ID'],
                        f'{AI_CORE_PREFIX}_CLIENT_SECRET': self.default_config[f'{AI_CORE_PREFIX}_CLIENT_SECRET'],
                        f'{AI_CORE_PREFIX}_BASE_URL': self.default_config[f'{AI_CORE_PREFIX}_BASE_URL'],
                        f'{AI_CORE_PREFIX}_AUTH_URL': self.default_config[f'{AI_CORE_PREFIX}_AUTH_URL'],
                    }
                ):
            credentials = fetch_credentials()
            self.assertEqual(credentials['client_id'], self.default_config[f'{AI_CORE_PREFIX}_CLIENT_ID'])
            self.assertEqual(credentials['client_secret'], self.default_config[f'{AI_CORE_PREFIX}_CLIENT_SECRET'])
            self.assertEqual(credentials['base_url'], self.default_config[f'{AI_CORE_PREFIX}_BASE_URL'] + '/v2')
            self.assertEqual(credentials['auth_url'],
                             self.default_config[f'{AI_CORE_PREFIX}_AUTH_URL'] + '/oauth/token')

            mock_logger.debug.assert_any_call("Using credentials from: environment variables")
            mock_logger.debug.assert_any_call("No resource_group found in any source")

    @patch('ai_core_sdk.credentials.logger')
    def test_fetch_credentials_from_config_file(self, mock_logger):
        mock_logger.debug = MagicMock()
        with patch.dict(os.environ, {CONFIG_FILE_ENV_VAR: str(self.temp_dir / 'config.json')}):
            fetch_credentials()

            mock_logger.debug.assert_any_call("Using credentials from: config file")
            mock_logger.debug.assert_any_call("No resource_group found in any source")

    @patch('ai_core_sdk.credentials.logger')
    def test_fetch_credentials_from_kwargs(self, mock_logger):
        mock_logger.debug = MagicMock()

        with patch.dict(
                os.environ,
                {
                    f'{AI_CORE_PREFIX}_CLIENT_ID': 'env-var-client-id',
                    f'{AI_CORE_PREFIX}_CLIENT_SECRET': 'env-var-client-secret',
                    f'{AI_CORE_PREFIX}_BASE_URL': 'env-var-base-url',
                    f'{AI_CORE_PREFIX}_RESOURCE_GROUP': 'env-var-resource-group',
                }
        ):
            credentials = fetch_credentials(
                client_id='kwarg-client',
                client_secret='kwarg-secret',
                base_url='kwarg-url',
                auth_url='kwarg-auth-url'
            )

            self.assertEqual(credentials['client_id'], 'kwarg-client')
            self.assertEqual(credentials['client_secret'], 'kwarg-secret')
            self.assertEqual(credentials['base_url'], 'kwarg-url/v2')
            self.assertEqual(credentials['auth_url'], 'kwarg-auth-url/oauth/token')
            self.assertEqual(credentials['resource_group'], 'env-var-resource-group')

            mock_logger.debug.assert_any_call("Using credentials from: kwargs")
            mock_logger.debug.assert_any_call(
                "Using resource_group '%s' from: %s",
                'env-var-resource-group',
                'environment variables'
            )

    @patch('ai_core_sdk.credentials.logger')
    def test_init_conf_permission_error(self, mock_logger):
        mock_logger.warning = MagicMock()

        # Create a config file and make it unreadable
        config_file = self.temp_dir / 'config_no_permission.json'
        with config_file.open('w') as f:
            json.dump(self.default_config, f)

        # Remove read permissions
        config_file.chmod(0o000)

        try:
            with patch.dict(os.environ, {CONFIG_FILE_ENV_VAR: str(config_file)}):
                conf = init_conf()
                # Should return empty config when permission is denied
                self.assertDictEqual(conf, {})
                # Should log a warning
                mock_logger.warning.assert_called_once()
                warning_call_args = mock_logger.warning.call_args[0]
                self.assertIn("Permission denied", warning_call_args[0])
                self.assertIn("File ignored", warning_call_args[0])
                self.assertEqual(warning_call_args[1], config_file)
        finally:
            # Restore permissions for cleanup in teardown
            config_file.chmod(0o644)

    @patch('ai_core_sdk.credentials.logger')
    def test_injecting_credential_values(self, mock_logger):
        mock_logger.debug = MagicMock()

        test_credential_values = [
            CredentialsValue(name='a'),
            CredentialsValue(name='b'),
            CredentialsValue(name='c')
        ]

        credentials = fetch_credentials(credential_values=test_credential_values, a='1', b='2', c='3', validate=False)

        self.assertEqual('1', credentials['a'])
        self.assertEqual('2', credentials['b'])
        self.assertEqual('3', credentials['c'])

        mock_logger.debug.assert_any_call("Using credentials from: kwargs")
