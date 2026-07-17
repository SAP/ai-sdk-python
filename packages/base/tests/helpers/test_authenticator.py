from typing import Tuple
from unittest import TestCase
from unittest.mock import MagicMock, patch

from ai_api_client_sdk.exception import AIAPIAuthenticatorException, AIAPIAuthenticatorInvalidRequestException, \
    AIAPIAuthenticatorAuthorizationException, AIAPIAuthenticatorServerException, \
    AIAPIAuthenticatorForbiddenException, AIAPIAuthenticatorMethodNotAllowedException, \
    AIAPIAuthenticatorTimeoutException
from ai_api_client_sdk.helpers.authenticator import Authenticator, PARAM_ERROR_MESSAGE


class ResponseMock:
    def __init__(self, json: dict, status_code: int, text: str = ''):
        self._json = json
        self.status_code = status_code
        self.text = text

    def json(self):
        return self._json


class TestAuthenticator(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.auth_url = 'test_auth_url'
        cls.client_id = 'test_client_id'
        cls.client_secret = 'test_client_secret'
        cls.cert_file_path = 'test_cert_file_path'
        cls.key_file_path = 'test_key_file_path'
        cls.cert_str = 'test_cert_str'
        cls.key_str = 'test_key_str'
        cls.token = 'test_token'
        cls.token_expire_time = '43200'

    @patch('ai_api_client_sdk.helpers.authenticator.requests')
    def test_authenticator(self, requests_mock):
        response_mock = MagicMock()
        response_mock.json.return_value = {'access_token': self.token, 'expires_in': self.token_expire_time}
        response_mock.status_code = 200
        requests_mock.post.return_value = response_mock
        data = {'grant_type': 'client_credentials', 'client_id': self.client_id, 'client_secret': self.client_secret}
        cut = Authenticator(auth_url=self.auth_url, client_id=self.client_id, client_secret=self.client_secret)
        generated_token = cut.get_token()
        requests_mock.post.assert_called_with(url=self.auth_url, data=data)
        self.assertEqual(f'Bearer {self.token}', generated_token)

    def test_no_secret_no_cert_raises_exception(self):
        with self.assertRaises(AIAPIAuthenticatorException) as cm:
            Authenticator(auth_url=self.auth_url, client_id=self.client_id)
        self.assertEqual(PARAM_ERROR_MESSAGE, cm.exception.error_message)

    def test_secret_cert_together_raises_exception(self):
        # cert and key file paths
        with self.assertRaises(AIAPIAuthenticatorException) as cm:
            Authenticator(auth_url=self.auth_url, client_id=self.client_id, client_secret='test_secret',
                          cert_file_path=self.cert_file_path)
        self.assertEqual(PARAM_ERROR_MESSAGE, cm.exception.error_message)

        with self.assertRaises(AIAPIAuthenticatorException) as cm:
            Authenticator(auth_url=self.auth_url, client_id=self.client_id, client_secret='test_secret',
                          key_file_path=self.key_file_path)
        self.assertEqual(PARAM_ERROR_MESSAGE, cm.exception.error_message)

        with self.assertRaises(AIAPIAuthenticatorException) as cm:
            Authenticator(auth_url=self.auth_url, client_id=self.client_id, client_secret='test_secret',
                          cert_file_path=self.cert_file_path, key_file_path=self.key_file_path)
        self.assertEqual(PARAM_ERROR_MESSAGE, cm.exception.error_message)

        # cert and key strings
        with self.assertRaises(AIAPIAuthenticatorException) as cm:
            Authenticator(auth_url=self.auth_url, client_id=self.client_id, client_secret='test_secret',
                          cert_str=self.cert_str)
        self.assertEqual(PARAM_ERROR_MESSAGE, cm.exception.error_message)

        with self.assertRaises(AIAPIAuthenticatorException) as cm:
            Authenticator(auth_url=self.auth_url, client_id=self.client_id, client_secret='test_secret',
                          key_str=self.key_str)
        self.assertEqual(PARAM_ERROR_MESSAGE, cm.exception.error_message)

        with self.assertRaises(AIAPIAuthenticatorException) as cm:
            Authenticator(auth_url=self.auth_url, client_id=self.client_id, client_secret='test_secret',
                          cert_str=self.cert_str, key_str=self.key_str)
        self.assertEqual(PARAM_ERROR_MESSAGE, cm.exception.error_message)

    def test_x509_str_file_path_together_raises_exception(self):
        with self.assertRaises(AIAPIAuthenticatorException) as cm:
            Authenticator(auth_url=self.auth_url, client_id=self.client_id, cert_str=self.cert_str,
                          key_file_path=self.key_file_path)
        self.assertEqual(PARAM_ERROR_MESSAGE, cm.exception.error_message)

        with self.assertRaises(AIAPIAuthenticatorException) as cm:
            Authenticator(auth_url=self.auth_url, client_id=self.client_id, cert_file_path=self.cert_file_path,
                          key_str=self.key_str)
        self.assertEqual(PARAM_ERROR_MESSAGE, cm.exception.error_message)

        with self.assertRaises(AIAPIAuthenticatorException) as cm:
            Authenticator(auth_url=self.auth_url, client_id=self.client_id, cert_str=self.cert_str,
                          key_str=self.key_str, key_file_path=self.key_file_path)
        self.assertEqual(PARAM_ERROR_MESSAGE, cm.exception.error_message)

        with self.assertRaises(AIAPIAuthenticatorException) as cm:
            Authenticator(auth_url=self.auth_url, client_id=self.client_id, cert_str=self.cert_str,
                          key_str=self.key_str, cert_file_path=self.cert_file_path)
        self.assertEqual(PARAM_ERROR_MESSAGE, cm.exception.error_message)

        with self.assertRaises(AIAPIAuthenticatorException) as cm:
            Authenticator(auth_url=self.auth_url, client_id=self.client_id, cert_str=self.cert_str,
                          cert_file_path=self.cert_file_path, key_file_path=self.key_file_path)
        self.assertEqual(PARAM_ERROR_MESSAGE, cm.exception.error_message)

        with self.assertRaises(AIAPIAuthenticatorException) as cm:
            Authenticator(auth_url=self.auth_url, client_id=self.client_id, key_str=self.key_str,
                          cert_file_path=self.cert_file_path, key_file_path=self.key_file_path)
        self.assertEqual(PARAM_ERROR_MESSAGE, cm.exception.error_message)

    def test_incomplete_x509_creds_raise_exception(self):
        with self.assertRaises(AIAPIAuthenticatorException) as cm:
            Authenticator(auth_url=self.auth_url, client_id=self.client_id, cert_str=self.cert_str)
        self.assertEqual(PARAM_ERROR_MESSAGE, cm.exception.error_message)

        with self.assertRaises(AIAPIAuthenticatorException) as cm:
            Authenticator(auth_url=self.auth_url, client_id=self.client_id, key_str=self.key_str)
        self.assertEqual(PARAM_ERROR_MESSAGE, cm.exception.error_message)

        with self.assertRaises(AIAPIAuthenticatorException) as cm:
            Authenticator(auth_url=self.auth_url, client_id=self.client_id, cert_file_path=self.cert_file_path)
        self.assertEqual(PARAM_ERROR_MESSAGE, cm.exception.error_message)

        with self.assertRaises(AIAPIAuthenticatorException) as cm:
            Authenticator(auth_url=self.auth_url, client_id=self.client_id, key_file_path=self.key_file_path)
        self.assertEqual(PARAM_ERROR_MESSAGE, cm.exception.error_message)

    @patch('ai_api_client_sdk.helpers.authenticator.requests')
    def test_with_x509_file_path(self, requests_mock):
        requests_mock.post.return_value = ResponseMock(
            {'access_token': self.token, 'expires_in': self.token_expire_time}, 200)
        data = {'grant_type': 'client_credentials', 'client_id': self.client_id}
        cut = Authenticator(auth_url=self.auth_url, client_id=self.client_id, cert_file_path=self.cert_file_path,
                            key_file_path=self.key_file_path)
        generated_token = cut.get_token()
        requests_mock.post.assert_called_with(url=self.auth_url, data=data,
                                              cert=(self.cert_file_path, self.key_file_path))
        self.assertEqual(f'Bearer {self.token}', generated_token)

    def _requests_post_mock(self, url: str, data: dict, cert: Tuple[str, str]):
        expected_data = {'grant_type': 'client_credentials', 'client_id': self.client_id}
        self.assertEqual(self.auth_url, url)
        self.assertEqual(expected_data, data)
        cert_file_path, key_file_path = cert
        with open(cert_file_path) as f:
            self.assertEqual(self.cert_str, f.read())
        with open(key_file_path) as f:
            self.assertEqual(self.key_str, f.read())
        return ResponseMock({'access_token': self.token, 'expires_in': self.token_expire_time}, 200)

    @patch('ai_api_client_sdk.helpers.authenticator.requests')
    def test_with_x509_str(self, requests_mock):
        requests_mock.post = self._requests_post_mock
        a = Authenticator(auth_url=self.auth_url, client_id=self.client_id, cert_str=self.cert_str,
                          key_str=self.key_str)
        generated_token = a.get_token()
        self.assertEqual(f'Bearer {self.token}', generated_token)

    @patch('ai_api_client_sdk.helpers.authenticator.requests')
    def test_error(self, requests_mock):
        requests_mock.post.side_effect = Exception
        a = Authenticator(auth_url=self.auth_url, client_id=self.client_id, client_secret=self.client_secret)
        with self.assertRaises(AIAPIAuthenticatorException):
            a.get_token()
        data = {'grant_type': 'client_credentials', 'client_id': self.client_id, 'client_secret': self.client_secret}
        requests_mock.post.assert_called_with(url=self.auth_url, data=data)

    @patch('ai_api_client_sdk.helpers.authenticator.requests')
    def test_get_token_raises_invalid_request_exception(self, requests_mock):
        self._do_test_get_token_raises_exception(
            requests_mock=requests_mock,
            status_code=400,
            error_msg="Invalid request",
            exception_class=AIAPIAuthenticatorInvalidRequestException,
            expected_post_calls=1,
        )

    @patch('ai_api_client_sdk.helpers.authenticator.requests')
    def test_get_token_raises_unauthorized_exception(self, requests_mock):
        self._do_test_get_token_raises_exception(
            requests_mock=requests_mock,
            status_code=401,
            error_msg="Unauthorized",
            exception_class=AIAPIAuthenticatorAuthorizationException,
            expected_post_calls=1,
        )

    @patch('ai_api_client_sdk.helpers.authenticator.requests')
    def test_get_token_raises_forbidden_exception(self, requests_mock):
        self._do_test_get_token_raises_exception(
            requests_mock=requests_mock,
            status_code=403,
            error_msg="Forbidden",
            exception_class=AIAPIAuthenticatorForbiddenException,
            expected_post_calls=1,
        )

    @patch('ai_api_client_sdk.helpers.authenticator.requests')
    def test_get_token_raises_method_not_allowed_exception(self, requests_mock):
        self._do_test_get_token_raises_exception(
            requests_mock=requests_mock,
            status_code=405,
            error_msg="Method not allowed",
            exception_class=AIAPIAuthenticatorMethodNotAllowedException,
            expected_post_calls=1,
        )

    @patch('ai_api_client_sdk.helpers.authenticator.requests')
    def test_get_token_raises_timeout_exception(self, requests_mock):
        self._do_test_get_token_raises_exception(
            requests_mock=requests_mock,
            status_code=408,
            error_msg="Request timeout",
            exception_class=AIAPIAuthenticatorTimeoutException,
            expected_post_calls=4,
        )

    @patch('ai_api_client_sdk.helpers.authenticator.requests')
    def test_get_token_raises_server_exception(self, requests_mock):
        self._do_test_get_token_raises_exception(
            requests_mock=requests_mock,
            status_code=500,
            error_msg="Server error",
            exception_class=AIAPIAuthenticatorServerException,
            expected_post_calls=4,
        )

    @patch('ai_api_client_sdk.helpers.authenticator.requests')
    def test_get_token_raises_exception(self, requests_mock):
        self._do_test_get_token_raises_exception(
            requests_mock=requests_mock,
            status_code=200,
            error_msg="Ok",
            exception_class=AIAPIAuthenticatorException,
            expected_post_calls=1,
        )

    @patch('ai_api_client_sdk.helpers.authenticator.requests')
    def test_token_is_cached(self, requests_mock):
        token = 'test_token'
        expires_in = '43200' # 12h
        response_mock = MagicMock()
        response_mock.json.return_value = {'access_token': token, 'expires_in': expires_in}
        response_mock.status_code = 200
        requests_mock.post.return_value = response_mock
        data = {'grant_type': 'client_credentials', 'client_id': self.client_id, 'client_secret': self.client_secret}
        cut = Authenticator(auth_url=self.auth_url, client_id=self.client_id, client_secret=self.client_secret)
        generated_token = cut.get_token()
        generated_token = cut.get_token()
        requests_mock.post.assert_called_once()
        requests_mock.post.assert_called_with(url=self.auth_url, data=data)
        self.assertEqual(f'Bearer {token}', generated_token)

    @patch('ai_api_client_sdk.helpers.authenticator.requests')
    def test_token_is_valid_but_refresh(self, requests_mock):
        token = 'test_token'
        expires_in = '3600'  # 1h
        response_mock = MagicMock()
        response_mock.json.return_value = {'access_token': token, 'expires_in': expires_in}
        response_mock.status_code = 200
        requests_mock.post.return_value = response_mock
        data = {'grant_type': 'client_credentials', 'client_id': self.client_id, 'client_secret': self.client_secret}
        cut = Authenticator(auth_url=self.auth_url, client_id=self.client_id, client_secret=self.client_secret)
        generated_token = cut.get_token()
        generated_token = cut.get_token()
        requests_mock.post.assert_called_with(url=self.auth_url, data=data)
        self.assertEqual(f'Bearer {token}', generated_token)
        self.assertEqual(2, requests_mock.post.call_count)

    @patch('ai_api_client_sdk.helpers.authenticator.requests')
    def test_token_is_expired(self, requests_mock):
        token = 'test_token'
        expires_in = '0'
        response_mock = MagicMock()
        response_mock.json.return_value = {'access_token': token, 'expires_in': expires_in}
        response_mock.status_code = 200
        requests_mock.post.return_value = response_mock
        data = {'grant_type': 'client_credentials', 'client_id': self.client_id, 'client_secret': self.client_secret}
        cut = Authenticator(auth_url=self.auth_url, client_id=self.client_id, client_secret=self.client_secret)
        generated_token = cut.get_token()
        generated_token = cut.get_token()
        requests_mock.post.assert_called_with(url=self.auth_url, data=data)
        self.assertEqual(f'Bearer {token}', generated_token)
        self.assertEqual(2, requests_mock.post.call_count)

    def _do_test_get_token_raises_exception(
        self,
        requests_mock,
        status_code,
        error_msg,
        exception_class,
        expected_post_calls: int,
    ):
        response_mock = MagicMock()
        response_mock.status_code = status_code
        response_mock.text = error_msg
        response_mock.json.side_effect = Exception
        requests_mock.post.return_value = response_mock

        authenticator = Authenticator(
            auth_url=self.auth_url,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        with patch('ai_api_client_sdk.helpers.authenticator.time.sleep') as sleep_mock:
            with self.assertRaises(exception_class) as exc_class:
                authenticator.get_token()

            data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
            }

            self.assertEqual(expected_post_calls, requests_mock.post.call_count)
            requests_mock.post.assert_called_with(url=self.auth_url, data=data)

            if expected_post_calls == 1:
                sleep_mock.assert_not_called()
            else:
                self.assertEqual(expected_post_calls - 1, sleep_mock.call_count)

        self.assertEqual('Could not retrieve Authorization token', exc_class.exception.description)
        self.assertEqual(error_msg, exc_class.exception.error_message)
        if status_code // 100 != 2:
            self.assertEqual(exc_class.exception.status_code, status_code)
        else:
            self.assertEqual(exc_class.exception.status_code, 500)
