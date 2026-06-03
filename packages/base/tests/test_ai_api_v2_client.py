import os
from unittest import TestCase

from ai_api_client_sdk.ai_api_v2_client import AIAPIV2Client, AUTH_PARAM_ERROR_MESSAGE
from ai_api_client_sdk.helpers.constants import SKIP_AUTH_ENV_VAR
from ai_api_client_sdk.exception import AIAPIAuthenticatorException


class TestAIAPIV2Client(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.base_url = 'test_base_url'
        cls.auth_url = 'test_auth_url'
        cls.client_id = 'test_client_id'
        cls.client_secret = 'test_client_secret'
        cls.cert_str = 'test_cert_str'
        cls.key_str = 'test_key_str'
        cls.cert_file_path = 'cert_file_path'
        cls.key_file_path = 'key_file_path'

    @staticmethod
    def token_generator():
        return 'test_token'

    def test_no_secret_no_cert_raises_exception(self):
        with self.assertRaises(AIAPIAuthenticatorException) as cm:
            c = AIAPIV2Client(base_url=self.base_url, auth_url=self.auth_url)
        self.assertTrue('client_id' in cm.exception.error_message)

    def test_happy_path_client_secret(self):
        c = AIAPIV2Client(base_url=self.base_url, auth_url=self.auth_url, client_id=self.client_id,
                          client_secret=self.client_secret)
        self.assertIsNotNone(c.rest_client)

    def test_happy_path_token_creator(self):
        c = AIAPIV2Client(base_url=self.base_url, token_creator=self.token_generator)
        self.assertIsNotNone(c.rest_client)

    def test_set_client_type_header(self):
        c = AIAPIV2Client(base_url=self.base_url, token_creator=self.token_generator, client_type='test_client_type')
        self.assertIsNotNone(c.rest_client)
        self.assertEqual(c.rest_client.headers['AI-Client-Type'], 'test_client_type')

    def test_happy_path_with_x509_str(self):
        c = AIAPIV2Client(base_url=self.base_url, auth_url=self.auth_url, client_id=self.client_id,
                          cert_str=self.cert_str, key_str=self.key_str)
        self.assertIsNotNone(c.rest_client)

    def test_happy_path_with_x509_file_path(self):
        c = AIAPIV2Client(base_url=self.base_url, auth_url=self.auth_url, client_id=self.client_id,
                          cert_file_path=self.cert_file_path, key_file_path=self.key_file_path)
        self.assertIsNotNone(c.rest_client)

    def test_token_creator_with_auth_parameters_raises_exception(self):
        with self.assertRaises(AIAPIAuthenticatorException) as cm:
            AIAPIV2Client(base_url=self.base_url, token_creator=self.token_generator, auth_url=self.auth_url)
        self.assertEqual(AUTH_PARAM_ERROR_MESSAGE, cm.exception.error_message)

        with self.assertRaises(AIAPIAuthenticatorException) as cm:
            AIAPIV2Client(base_url=self.base_url, token_creator=self.token_generator, cert_str=self.cert_str)
        self.assertEqual(AUTH_PARAM_ERROR_MESSAGE, cm.exception.error_message)

        with self.assertRaises(AIAPIAuthenticatorException) as cm:
            AIAPIV2Client(base_url=self.base_url, token_creator=self.token_generator, key_file_path=self.key_file_path)
        self.assertEqual(AUTH_PARAM_ERROR_MESSAGE, cm.exception.error_message)

    def test_client_secret_with_x509_raises_exception(self):
        with self.assertRaises(AIAPIAuthenticatorException) as cm:
            AIAPIV2Client(base_url=self.base_url, auth_url=self.auth_url, client_id=self.client_id,
                          client_secret=self.client_secret, cert_file_path=self.cert_file_path)
        self.assertEqual(AUTH_PARAM_ERROR_MESSAGE, cm.exception.error_message)

        with self.assertRaises(AIAPIAuthenticatorException) as cm:
            AIAPIV2Client(base_url=self.base_url, auth_url=self.auth_url, client_id=self.client_id,
                          client_secret=self.client_secret, key_str=self.key_str)
        self.assertEqual(AUTH_PARAM_ERROR_MESSAGE, cm.exception.error_message)

    def test_x509_str_with_file_path_raises_exception(self):
        with self.assertRaises(AIAPIAuthenticatorException) as cm:
            AIAPIV2Client(base_url=self.base_url, auth_url=self.auth_url, client_id=self.client_id,
                          cert_file_path=self.cert_file_path, key_file_path=self.key_file_path, cert_str=self.cert_str)
        self.assertEqual(AUTH_PARAM_ERROR_MESSAGE, cm.exception.error_message)

        with self.assertRaises(AIAPIAuthenticatorException) as cm:
            AIAPIV2Client(base_url=self.base_url, auth_url=self.auth_url, client_id=self.client_id,
                          key_file_path=self.key_file_path, cert_str=self.cert_str, key_str=self.key_str)
        self.assertEqual(AUTH_PARAM_ERROR_MESSAGE, cm.exception.error_message)

        with self.assertRaises(AIAPIAuthenticatorException) as cm:
            AIAPIV2Client(base_url=self.base_url, auth_url=self.auth_url, client_id=self.client_id,
                          cert_file_path=self.cert_file_path, key_file_path=self.key_file_path, cert_str=self.cert_str,
                          key_str=self.key_str)
        self.assertEqual(AUTH_PARAM_ERROR_MESSAGE, cm.exception.error_message)

    def test_skip_authorization(self):
        with self.assertRaises(AIAPIAuthenticatorException) as cm:
            c = AIAPIV2Client(base_url=self.base_url)
        self.assertTrue('client_id' in cm.exception.error_message)

        # Set SKIP_AUTHORIZATION to 'true'
        os.environ[SKIP_AUTH_ENV_VAR] = 'true'
        c = AIAPIV2Client(base_url=self.base_url)
        self.assertIsNotNone(c.rest_client)

        # Clean up
        del os.environ[SKIP_AUTH_ENV_VAR]
