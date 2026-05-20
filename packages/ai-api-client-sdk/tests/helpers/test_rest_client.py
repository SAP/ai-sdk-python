import json
import os
from unittest import TestCase
from unittest.mock import MagicMock, patch

from ai_api_client_sdk.exception import AIAPIAuthorizationException, AIAPIInvalidRequestException, \
    AIAPINotFoundException, AIAPIPreconditionFailedException, AIAPIServerException
from ai_api_client_sdk.helpers.constants import DEBUG_ENV_VAR_NAME, SKIP_AUTH_ENV_VAR, Timeouts
from ai_api_client_sdk.helpers.rest_client import RestClient

REQUESTS_PATCH_STRING = 'ai_api_client_sdk.helpers.rest_client.requests'

class TestRestClient(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base_url = 'test_base_url'
        cls.resource_group = 'test_resource_group'
        cls.client_type = 'test_client_type'
        cls.path = '/test_path'
        cls.url = f'{cls.base_url}{cls.path}'
        cls.params = {'param1': 'value1'}
        cls.body = {'key': 'value'}
        cls.headers = {'AI-Resource-Group': cls.resource_group, 'Authorization': cls.get_token(),
                       'AI-Client-Type': cls.client_type}
        cls.response_json = {'response': 'OK'}
        cls.response_mock = cls.create_response_mock(200, cls.response_json)
        cls.rest_client = RestClient(base_url=cls.base_url, get_token=cls.get_token, resource_group=cls.resource_group,
                                     client_type=cls.client_type)

    @staticmethod
    def create_response_mock(status_code, json_dict, text=None):
        response_mock = MagicMock()
        response_mock.status_code = status_code
        response_mock.json.return_value = json_dict
        if text is None:
            response_mock.text = json.dumps(json_dict)
        else:
            response_mock.text = text
        return response_mock

    @staticmethod
    def create_error_json(message=None, code=None, request_id=None, details=None):
        error_json = {
            'error': {
                'message': message if message else 'Error message',
                'code': code if code else 'Error code',
                'requestId': request_id if request_id else 'request_id'
            }
        }
        if details:
            error_json['error']['details'] = details
        return error_json

    def create_error_description(self, path=None):
        path = path or self.path
        return f'Failed to get {path}'

    def assert_server_exception(self, exception: AIAPIServerException, status_code: int, error_description: str = None,
                                error_json: dict = None, response_text: str = None):
        self.assertEqual(status_code, exception.status_code)
        error_description = error_description or self.create_error_description()
        self.assertEqual(error_description, exception.description)
        if response_text:
            self.assertEqual(response_text, exception.error_message)
        if error_json:
            self.assertEqual(error_json['error']['message'], exception.error_message)
            self.assertEqual(error_json['error']['code'], exception.error_code)
            self.assertEqual(error_json['error']['requestId'], exception.request_id)
            self.assertEqual(error_json['error'].get('details'), exception.details)

    @staticmethod
    def get_token():
        return 'test_token'

    @patch(REQUESTS_PATCH_STRING)
    def test_get(self, requests_mock):
        request_session = MagicMock()
        request_session.get.return_value = self.response_mock
        requests_mock.Session.return_value = request_session
        r_json = self.rest_client.get(path=self.path, params=self.params)
        request_session.get.assert_called_with(url=self.url, params=self.params, json=None, headers=self.headers,
                                               timeout=(60, 60))
        self.assertEqual(self.response_json, r_json)

    @patch(REQUESTS_PATCH_STRING)
    def test_debug_log_api_call_enabled(self, requests_mock):
        os.environ[DEBUG_ENV_VAR_NAME] = 'True'
        request_session = MagicMock()
        request_session.post.return_value = self.response_mock
        requests_mock.Session.return_value = request_session

        with self.assertLogs(self.rest_client.logger, level='DEBUG') as cm:
            r_json = self.rest_client.post(self.path, self.body, self.headers, self.resource_group)
            self.assertEqual(self.response_json, r_json)
            self.assertEqual(2, len(cm.output))
            self.assertTrue(self.resource_group in cm.output[0])
            self.assertTrue(self.path in cm.output[0])
            self.assertTrue(self.url in cm.output[0])
            self.assertTrue(str(self.body) in cm.output[0])
            token = self.get_token()
            self.assertFalse(token in cm.output[0])
            for k, v in self.response_json.items():
                self.assertTrue(k in cm.output[1])
                self.assertTrue(v in cm.output[1])

    @patch(REQUESTS_PATCH_STRING)
    def test_debug_log_api_call_disabled(self, requests_mock):
        os.environ[DEBUG_ENV_VAR_NAME] = 'False'
        request_session = MagicMock()
        request_session.get.return_value = self.response_mock
        requests_mock.Session.return_value = request_session

        error_msg = None
        try:
            with self.assertLogs(self.rest_client.logger, level='DEBUG') as cm:
                self.rest_client._handle_request('get', self.path, self.params)
                if len(cm.output) > 0:
                    error_msg = 'No logs should be generated when env var DEBUG is not set.'
        except AssertionError:
            # assertLogs raises AssertionError if no logs are generated
            pass

        if error_msg:
            self.fail(error_msg)

    @patch(REQUESTS_PATCH_STRING)
    def test_get_empty_body(self, requests_mock):
        request_session = MagicMock()
        request_session.get.return_value = self.create_response_mock(200, None, '')
        request_session.get.return_value.json.side_effect = json.decoder.JSONDecodeError('msg', 'doc', 1)
        requests_mock.Session.return_value = request_session
        r_json = self.rest_client.get(path=self.path, params=self.params)
        request_session.get.assert_called_with(url=self.url, params=self.params, json=None, headers=self.headers,
                                               timeout=(60, 60))
        self.assertEqual('', r_json)

    @patch(REQUESTS_PATCH_STRING)
    def test_post(self, requests_mock):
        request_session = MagicMock()
        request_session.post.return_value = self.response_mock
        requests_mock.Session.return_value = request_session
        r_json = self.rest_client.post(path=self.path, body=self.body)
        request_session.post.assert_called_with(url=self.url, params=None, json=self.body, headers=self.headers,
                                                timeout=(60, 60))
        self.assertEqual(self.response_json, r_json)

    @patch(REQUESTS_PATCH_STRING)
    def test_post_empty_body(self, requests_mock):
        request_session = MagicMock()
        request_session.post.return_value = self.create_response_mock(200, None, '')
        request_session.post.return_value.json.side_effect = json.decoder.JSONDecodeError('msg', 'doc', 1)
        requests_mock.Session.return_value = request_session
        r_json = self.rest_client.post(path=self.path, body=self.body)
        request_session.post.assert_called_with(url=self.url, params=None, json=self.body, headers=self.headers,
                                                timeout=(60, 60))
        self.assertEqual('', r_json)

    @patch(REQUESTS_PATCH_STRING)
    def test_patch(self, requests_mock):
        request_session = MagicMock()
        request_session.patch.return_value = self.response_mock
        requests_mock.Session.return_value = request_session
        r_json = self.rest_client.patch(path=self.path, body=self.body)
        request_session.patch.assert_called_with(url=self.url, params=None, json=self.body, headers=self.headers,
                                                 timeout=(60, 60))
        self.assertEqual(self.response_json, r_json)

    @patch(REQUESTS_PATCH_STRING)
    def test_patch_empty_body(self, requests_mock):
        request_session = MagicMock()
        request_session.patch.return_value = self.create_response_mock(200, None, '')
        request_session.patch.return_value.json.side_effect = json.decoder.JSONDecodeError('msg', 'doc', 1)
        requests_mock.Session.return_value = request_session
        r_json = self.rest_client.patch(path=self.path, body=self.body)
        request_session.patch.assert_called_with(url=self.url, params=None, json=self.body, headers=self.headers,
                                                 timeout=(60, 60))
        self.assertEqual('', r_json)

    @patch(REQUESTS_PATCH_STRING)
    def test_delete(self, requests_mock):
        request_session = MagicMock()
        request_session.delete.return_value = self.response_mock
        requests_mock.Session.return_value = request_session
        r_json = self.rest_client.delete(path=self.path)
        request_session.delete.assert_called_with(url=self.url, params=None, json=None, headers=self.headers,
                                                  timeout=(60, 60))
        self.assertEqual(self.response_json, r_json)

    @patch(REQUESTS_PATCH_STRING)
    def test_delete_empty_body(self, requests_mock):
        request_session = MagicMock()
        request_session.delete.return_value = self.create_response_mock(200, None, '')
        request_session.delete.return_value.json.side_effect = json.decoder.JSONDecodeError('msg', 'doc', 1)
        requests_mock.Session.return_value = request_session
        r_json = self.rest_client.delete(path=self.path)
        request_session.delete.assert_called_with(url=self.url, params=None, json=None, headers=self.headers,
                                                  timeout=(60, 60))
        self.assertEqual('', r_json)

    @patch(REQUESTS_PATCH_STRING)
    def test_client_type_from_parameter(self, requests_mock):
        request_session = MagicMock()
        request_session.get.return_value = self.response_mock
        requests_mock.Session.return_value = request_session
        self.rest_client.get(path=self.path)
        headers = self.headers.copy()
        request_session.get.assert_called_with(url=self.url, params=None, json=None, headers=headers,
                                               timeout=(Timeouts.CONNECT_TIMEOUT.value, Timeouts.READ_TIMEOUT.value))

    @patch(REQUESTS_PATCH_STRING)
    def test_client_type_from_env_var(self, requests_mock):
        backup = os.environ.get('AI_CLIENT_TYPE', None)
        try:
            env_client_type = 'env_client_type'
            os.environ['AI_CLIENT_TYPE'] = env_client_type
            rest_client = RestClient(base_url=self.base_url, get_token=self.get_token,
                                     resource_group=self.resource_group)
            request_session = MagicMock()
            request_session.get.return_value = self.response_mock
            requests_mock.Session.return_value = request_session
            rest_client.get(path=self.path)
            headers = self.headers.copy()
            headers['AI-Client-Type'] = env_client_type
            request_session.get.assert_called_with(url=self.url, params=None, json=None, headers=headers,
                                                   timeout=(Timeouts.CONNECT_TIMEOUT.value, Timeouts.READ_TIMEOUT.value))
        finally:
            if backup is not None:
                os.environ['AI_CLIENT_TYPE'] = backup
            else:
                del os.environ['AI_CLIENT_TYPE']

    @patch(REQUESTS_PATCH_STRING)
    def test_client_type_env_var_precedence(self, requests_mock):
        try:
            env_client_type = 'env_client_type'
            os.environ['AI_CLIENT_TYPE'] = env_client_type
            rest_client = RestClient(base_url=self.base_url, get_token=self.get_token,
                                     resource_group=self.resource_group, client_type='param_client_type')
            request_session = MagicMock()
            request_session.get.return_value = self.response_mock
            requests_mock.Session.return_value = request_session
            rest_client.get(path=self.path)
            headers = self.headers.copy()
            headers['AI-Client-Type'] = env_client_type
            request_session.get.assert_called_with(url=self.url, params=None, json=None, headers=headers,
                                                   timeout=(Timeouts.CONNECT_TIMEOUT.value, Timeouts.READ_TIMEOUT.value))
        finally:
            del os.environ['AI_CLIENT_TYPE']

    @patch(REQUESTS_PATCH_STRING)
    def test_no_client_type(self, requests_mock):
        rest_client = RestClient(base_url=self.base_url, get_token=self.get_token,
                                 resource_group=self.resource_group)
        request_session = MagicMock()
        request_session.get.return_value = self.response_mock
        requests_mock.Session.return_value = request_session
        rest_client.get(path=self.path)
        headers = self.headers.copy()
        del headers['AI-Client-Type']
        request_session.get.assert_called_with(url=self.url, params=None, json=None, headers=headers,
                                               timeout=(Timeouts.CONNECT_TIMEOUT.value, Timeouts.READ_TIMEOUT.value))

    @patch(REQUESTS_PATCH_STRING)
    def test_get_with_resource_group(self, requests_mock):
        request_session = MagicMock()
        request_session.get.return_value = self.response_mock
        requests_mock.Session.return_value = request_session
        new_rg = 'new_resource_group'
        headers = self.headers.copy()
        headers['AI-Resource-Group'] = new_rg
        r_json = self.rest_client.get(path=self.path, resource_group=new_rg)
        request_session.get.assert_called_with(url=self.url, params=None, json=None, headers=headers, timeout=(60, 60))
        self.assertEqual(self.response_json, r_json)

    @patch(REQUESTS_PATCH_STRING)
    def test_camelize_decamelize(self, requests_mock):
        body = {'body_key': 'body_value'}
        c_body = {'bodyKey': 'body_value'}
        params = {'param_key': 'param_value'}
        c_params = {'paramKey': 'param_value'}
        response_json = {'responseKey': 'response_value'}
        d_response_json = {'response_key': 'response_value'}
        request_session = MagicMock()
        request_session.post.return_value = self.create_response_mock(200, response_json)
        requests_mock.Session.return_value = request_session
        r_json = self.rest_client.post(path=self.path, body=body)
        request_session.post.assert_called_with(url=self.url, params=None, json=c_body, headers=self.headers,
                                                timeout=(60, 60))
        self.assertEqual(d_response_json, r_json)
        request_session.get.return_value = self.create_response_mock(200, response_json)
        r_json = self.rest_client.get(path=self.path, params=params)
        request_session.get.assert_called_with(url=self.url, params=c_params, json=None, headers=self.headers,
                                               timeout=(60, 60))
        self.assertEqual(d_response_json, r_json)

    @patch(REQUESTS_PATCH_STRING)
    def test_not_camelize_body(self, requests_mock):
        body = {'body_key': 'body_value'}

        response_json = {'responseKey': 'response_value'}

        request_session = MagicMock()
        request_session.post.return_value = self.create_response_mock(200, response_json)
        requests_mock.Session.return_value = request_session

        kwargs = {'convert_body_to_camel_case': False}
        self.rest_client.post(path=self.path, body=body, **kwargs)
        request_session.post.assert_called_with(url=self.url, params=None, json=body, headers=self.headers,
                                                timeout=(60, 60))

    @patch(REQUESTS_PATCH_STRING)
    def test_not_camelize_params(self, requests_mock):
        request_session = MagicMock()
        params = {'param_key': 'param_value'}
        kwargs = {'convert_params_to_camel_case': False}
        request_session.get.return_value = self.response_mock
        requests_mock.Session.return_value = request_session
        r_json = self.rest_client.get(path=self.path, params=params, **kwargs)
        request_session.get.assert_called_with(url=self.url, params=params, json=None, headers=self.headers,
                                               timeout=(60, 60))
        self.assertEqual(self.response_json, r_json)

    @patch(REQUESTS_PATCH_STRING)
    def test_authorization_exception(self, requests_mock):
        request_session = MagicMock()
        request_session.get.return_value = self.create_response_mock(401, {})
        requests_mock.Session.return_value = request_session
        with self.assertRaises(AIAPIAuthorizationException) as cm:
            self.rest_client.get(path=self.path)
        request_session.get.assert_called_with(url=self.url, params=None, json=None, headers=self.headers,
                                               timeout=(60, 60))
        self.assertEqual(f'Failed to get {self.path}', cm.exception.description)

    @patch(REQUESTS_PATCH_STRING)
    def test_request_exception(self, requests_mock):
        request_session = MagicMock()
        request_session.get.side_effect = Exception
        requests_mock.Session.return_value = request_session
        with self.assertRaises(Exception):
            self.rest_client.get(path=self.path)

    @patch(REQUESTS_PATCH_STRING)
    def test_server_exception(self, requests_mock):
        status_code = 500
        response_text = 'error_text'
        request_session = MagicMock()
        request_session.get.return_value = self.create_response_mock(status_code, {}, response_text)
        requests_mock.Session.return_value = request_session
        with self.assertRaises(AIAPIServerException) as cm:
            self.rest_client.get(path=self.path)
        self.assert_server_exception(cm.exception, status_code, response_text=response_text)

    @patch(REQUESTS_PATCH_STRING)
    def test_invalid_request_exception(self, requests_mock):
        status_code = 400
        error_json = self.create_error_json(message='Invalid Request', details='Invalid')
        request_session = MagicMock()
        request_session.get.return_value = self.create_response_mock(status_code, error_json)
        requests_mock.Session.return_value = request_session
        with self.assertRaises(AIAPIInvalidRequestException) as cm:
            self.rest_client.get(path=self.path)
        self.assert_server_exception(cm.exception, status_code, error_json=error_json)

    @patch(REQUESTS_PATCH_STRING)
    def test_not_found_exception(self, requests_mock):
        status_code = 404
        error_json = self.create_error_json(message='Not Found')
        request_session = MagicMock()
        request_session.get.return_value = self.create_response_mock(status_code, error_json)
        requests_mock.Session.return_value = request_session
        with self.assertRaises(AIAPINotFoundException) as cm:
            self.rest_client.get(path=self.path)
        self.assert_server_exception(cm.exception, status_code, error_json=error_json)

    @patch(REQUESTS_PATCH_STRING)
    def test_precondition_failed_exception(self, requests_mock):
        status_code = 412
        error_json = self.create_error_json(message='Precondition Failed')
        request_session = MagicMock()
        request_session.get.return_value = self.create_response_mock(status_code, error_json)
        requests_mock.Session.return_value = request_session
        with self.assertRaises(AIAPIPreconditionFailedException) as cm:
            self.rest_client.get(path=self.path)
        self.assert_server_exception(cm.exception, status_code, error_json=error_json)

    @patch(REQUESTS_PATCH_STRING)
    def test_kwargs(self, requests_mock):
        request_session = MagicMock()
        request_session.get.return_value = self.response_mock
        request_session.post.return_value = self.response_mock
        requests_mock.Session.return_value = request_session

        kwargs = {'a': True, 'b': 1, 'c': 'string'}

        rget_json = self.rest_client.get(path=self.path, params=self.params, headers=self.headers, **kwargs)
        request_session.get.assert_called_with(url=self.url, params=self.params, json=None, headers=self.headers,
                                                timeout=(Timeouts.CONNECT_TIMEOUT.value, Timeouts.READ_TIMEOUT.value),
                                                **kwargs)
        self.assertEqual(self.response_json, rget_json)

        rpost_json = self.rest_client.post(path=self.path, params=self.params, headers=self.headers, **kwargs)
        request_session.post.assert_called_with(url=self.url, params=self.params, json=None, headers=self.headers,
                                                timeout=(Timeouts.CONNECT_TIMEOUT.value, Timeouts.READ_TIMEOUT.value),
                                                **kwargs)
        self.assertEqual(self.response_json, rpost_json)

    @patch(REQUESTS_PATCH_STRING)
    def test_kwargs_error(self, requests_mock):
        status_code = 400
        error_json = self.create_error_json(message='Unexpected key', code=status_code)
        request_session = MagicMock()
        request_session.get.return_value = self.create_response_mock(status_code, error_json)
        requests_mock.Session.return_value = request_session
        kwargs = {'X': False}
        with self.assertRaises(AIAPIServerException) as cm:
            self.rest_client.get(path=self.path, **kwargs)
        self.assert_server_exception(cm.exception, status_code, error_json=error_json)

    @patch(REQUESTS_PATCH_STRING)
    def test_bytes_response(self, requests_mock):
        response_mock = MagicMock()
        response_mock.status_code = 200
        response_mock.content = b'response_bytes_content'
        request_session = MagicMock()
        request_session.get.return_value = response_mock
        requests_mock.Session.return_value = request_session
        r_json = self.rest_client.get(path=self.path, return_bytes_content=True)
        request_session.get.assert_called_with(url=self.url, params=None, json=None, headers=self.headers, timeout=(60, 60))
        self.assertEqual(b'response_bytes_content', r_json)

    @patch('ai_api_client_sdk.helpers.rest_client.requests')
    def test_skip_authorization_env_var(self, requests_mock):
        # Set SKIP_AUTHORIZATION to 'true'
        os.environ[SKIP_AUTH_ENV_VAR] = 'true'
        request_session = MagicMock()
        request_session.get.return_value = self.response_mock
        requests_mock.Session.return_value = request_session

        # Remove Authorization from headers to simulate default behavior
        headers = self.headers.copy()
        headers.pop('Authorization', None)

        # Call get without Authorization header
        r_json = self.rest_client.get(path=self.path, headers=headers)
        # Ensure Authorization header is NOT set
        called_headers = request_session.get.call_args[1]['headers']
        assert 'Authorization' not in called_headers
        self.assertEqual(self.response_json, r_json)

        # Clean up
        del os.environ[SKIP_AUTH_ENV_VAR]

        # Now test when SKIP_AUTHORIZATION is not set
        request_session.get.reset_mock()
        r_json = self.rest_client.get(path=self.path, headers=headers)
        called_headers = request_session.get.call_args[1]['headers']
        assert 'Authorization' in called_headers
        self.assertEqual(self.response_json, r_json)
