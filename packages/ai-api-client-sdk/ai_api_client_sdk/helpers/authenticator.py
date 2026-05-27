import os
import tempfile
from datetime import timedelta, datetime, timezone
from threading import Lock
from typing import Optional

import requests
import time
from requests.exceptions import ConnectionError

from ai_api_client_sdk.exception import AIAPIAuthenticatorException, AIAPIAuthenticatorInvalidRequestException, \
    AIAPIAuthenticatorAuthorizationException, AIAPIAuthenticatorServerException, \
    AIAPIAuthenticatorForbiddenException, AIAPIAuthenticatorMethodNotAllowedException, \
    AIAPIAuthenticatorTimeoutException
from ai_api_client_sdk.helpers import _is_all_none

PARAM_ERROR_MESSAGE = ('Either client_secret, or (cert_file_path, key_file_path) pair, '
                       'or (cert_str, key_str) pair need to be provided')
MAX_RETRY_ATTEMPTS_FOR_TOKEN = 3
BASE_DELAY_FOR_TOKEN_RETRY = 0.3


class Authenticator:
    """Authenticator class is implemented to retrieve and cache the authorization token from the xsuaa server

    :param auth_url: URL of the authorization endpoint. Should be the full URL (including /oauth/token)
    :type auth_url: str
    :param client_id: client id to be used for authorization
    :type client_id: str
    :param client_secret: client secret to be used for authorization, either client_secret or
        (cert_file_path and key_file_path) need to be provided, defaults to None
    :type client_secret: str, optional
    :param cert_str: certificate file content, needs to be provided alongside the key_str parameter, defaults to None
    :type cert_str: str, optional
    :param key_str: key file content, needs to be provided alongside the cert_str parameter, defaults to None
    :type key_str: str, optional
    :param cert_file_path: path to the certificate file, needs to be provided alongside the key_file_path parameter,
        defaults to None
    :type cert_file_path: str, optional
    :param key_file_path: path to the key file, needs to be provided alongside the cert_file_path parameter,
        defaults to None
    :type key_file_path: str, optional
    """

    def __init__(self, auth_url: str, client_id: str, client_secret: str = None, cert_str: str = None,
                 key_str: str = None, cert_file_path: str = None, key_file_path: str = None):
        self.url: str = auth_url
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.cert_str: str = cert_str.replace('\\n', '\n') if cert_str else None
        self.key_str: str = key_str.replace('\\n', '\n') if key_str else None
        self.cert_file_path: str = cert_file_path
        self.key_file_path: str = key_file_path
        if not ((client_secret is not None and _is_all_none(cert_str, key_str, cert_file_path, key_file_path))
                or (cert_file_path is not None and key_file_path is not None and _is_all_none(client_secret,
                                                                                                   cert_str, key_str))
                or (cert_str is not None and key_str is not None and _is_all_none(client_secret, cert_file_path,
                                                                                       key_file_path))):
            raise AIAPIAuthenticatorException(error_message=PARAM_ERROR_MESSAGE)
        self.token = None # Token Caching
        self.token_expiry_date = None
        self.lock = Lock() # Thread-Safe Lock

    def _request_token_with_cert_key_str(self, data: dict):
        with tempfile.TemporaryDirectory() as temp_dir:
            cert_file_path = os.path.join(temp_dir, f'cert.pem')
            key_file_path = os.path.join(temp_dir, f'key.pem')
            with open(cert_file_path, 'w') as f:
                f.write(self.cert_str)
            with open(key_file_path, 'w') as f:
                f.write(self.key_str)
            response = requests.post(url=self.url, data=data, cert=(cert_file_path, key_file_path))
        return response

    def _should_retry_token_retrieval_params(
            self, attempt: int,
            response: Optional[requests.Response] = None,
            status_code: Optional[int] = None,
            exp: Optional[Exception] = None
    ) -> dict:
        """
        Determines whether to retry the token retrieval operation based on the HTTP status code,
        number of attempts, or specific exceptions, and calculates the delay before the next retry.

        :param attempt: Current attempt number for the token retrieval.
        :type attempt: int
        :param response: HTTP response object related to the token retrieval, if available.
        :type response: Optional[requests.Response]
        :param status_code: HTTP status code from the token retrieval response, if available.
        :type status_code: Optional[int]
        :param exp: Exception raised during the token retrieval, if any.
        :type exp: Optional[Exception]

        :return: A dictionary containing:
            - ``should_retry`` (bool): Indicates whether the operation should be retried.
            - ``delay`` (float): The delay before the next retry attempt, if applicable.
        :rtype: dict
        """

        if status_code in [401, 403] or attempt == MAX_RETRY_ATTEMPTS_FOR_TOKEN:
            return {"should_retry": False,
                    "delay": 0}

        if status_code in [408, 502, 504] or (exp and isinstance(exp, ConnectionError)):
            return {"should_retry": True,
                    "delay": BASE_DELAY_FOR_TOKEN_RETRY * (2 ** attempt)}

        if status_code in [500, 503]:
            return {"should_retry": True,
                    "delay": BASE_DELAY_FOR_TOKEN_RETRY * (3 ** attempt)}

        if status_code == 429:
            return {"should_retry": True,
                    "delay": float(response.headers.get("Retry-After", 1))}

        return {"should_retry": False,
                "delay": 0}

    def _execute_token_request(self) -> requests.Response:
        """Executes a request to the xsuaa server to retrieve the token.

        :return: The response from the xsuaa server.
        :rtype: requests.Response

        :raises: class:`ai_api_client_sdk.exception.AIAPIAuthenticatorException` if an unexpected exception occurs"""
        data = {"grant_type": "client_credentials", "client_id": self.client_id}
        if self.client_secret:
            data["client_secret"] = self.client_secret
            return requests.post(url=self.url, data=data)
        if self.cert_str and self.key_str:
            return self._request_token_with_cert_key_str(data)
        if self.cert_file_path and self.key_file_path:
            return requests.post(url=self.url, data=data, cert=(self.cert_file_path, self.key_file_path))
        raise AIAPIAuthenticatorException(error_message=PARAM_ERROR_MESSAGE)

    def _sleep_before_retry(self, attempt: int, *, response: Optional[requests.Response] = None,
                            status_code: Optional[int] = None, exp: Optional[Exception] = None) -> bool:
        params = self._should_retry_token_retrieval_params(
            attempt=attempt,
            response=response,
            status_code=status_code,
            exp=exp,
        )
        if not params["should_retry"]:
            return False
        time.sleep(params["delay"])
        return True

    def _retrieve_token_with_retries(self) -> tuple[requests.Response, int, Optional[str]]:
        """Retrieves the token from the xsuaa server with retries.

        :return: A tuple containing: response, status_code, error_msg
        :rtype: tuple[requests.Response, int, Optional[str]]

        :raises: class:`ai_api_client_sdk.exception.AIAPIAuthenticatorException` if an unexpected exception occurs
        """
        attempt = 0
        error_msg: Optional[str] = None
        status_code = 0

        while status_code // 100 != 2:
            try:
                response = self._execute_token_request()
                status_code = response.status_code
                error_msg = response.text
            except AIAPIAuthenticatorException:
                raise
            except Exception as exception:  # pylint:disable=broad-except
                if self._sleep_before_retry(attempt, exp=exception):
                    attempt += 1
                    continue
                raise AIAPIAuthenticatorException(status_code=500, error_message=error_msg) from exception

            if self._sleep_before_retry(attempt, response=response, status_code=status_code):
                attempt += 1
                continue

            return response, status_code, error_msg

        return response, status_code, error_msg

    def _raise_for_status(self, status_code: int, error_msg: Optional[str]) -> None:
        """Raises an exception based on the HTTP status code received from the xsuaa server.
        :param status_code: The HTTP status code.
        :type status_code: int
        :param error_msg: The error message.
        :type error_msg: Optional[str]

        :raises: class:`ai_api_client_sdk.exception.AIAPIAuthenticatorInvalidRequestException` if the status code is 400
        :raises: class:`ai_api_client_sdk.exception.AIAPIAuthenticatorAuthorizationException` if the status code is 401
        :raises: class:`ai_api_client_sdk.exception.AIAPIAuthenticatorForbiddenException` if the status code is 403
        :raises: class:`ai_api_client_sdk.exception.AIAPIAuthenticatorMethodNotAllowedException` if the status code is 405
        :raises: class:`ai_api_client_sdk.exception.AIAPIAuthenticatorTimeoutException` if the status code is 408
        :raises: class:`ai_api_client_sdk.exception.AIAPIAuthenticatorServerException` if the status code is not 2XX
        """
        if status_code == 400:
            raise AIAPIAuthenticatorInvalidRequestException(error_message=error_msg)
        elif status_code == 401:
            raise AIAPIAuthenticatorAuthorizationException(error_message=error_msg)
        elif status_code == 403:
            raise AIAPIAuthenticatorForbiddenException(error_message=error_msg)
        elif status_code == 405:
            raise AIAPIAuthenticatorMethodNotAllowedException(error_message=error_msg)
        elif status_code == 408:
            raise AIAPIAuthenticatorTimeoutException(error_message=error_msg)
        elif status_code // 100 != 2:
            raise AIAPIAuthenticatorServerException(status_code=status_code, error_message=error_msg)

    def _update_token_from_response(self, response: requests.Response, error_msg: Optional[str]) -> None:
        """Updates the token from the response received from the xsuaa server.
        :param response: The response received from the xsuaa server.
        :type response: requests.Response
        :param error_msg: The error message received from the xsuaa server.
        :type error_msg: Optional[str]

        :raises: class:`ai_api_client_sdk.exception.AIAPIAuthenticatorException` if an unexpected exception occurs while
        """
        try:
            payload = response.json()
            access_token = payload["access_token"]
            self.token = f"Bearer {access_token}"
            self._calc_token_expiry_date(payload["expires_in"])
        except Exception as exception:  # pylint:disable=broad-except
            raise AIAPIAuthenticatorException(status_code=500, error_message=error_msg) from exception

    def get_token(self) -> str:
        """Retrieves the token from the xsuaa server or from cache when expiration date not reached.

        :raises: class:`ai_api_client_sdk.exception.AIAPIAuthenticatorException` if an unexpected exception occurs while
            trying to retrieve the token
        :return: The Bearer token
        :rtype: str
        """
        with self.lock: # Thread-Safe
            if self._should_refresh_token():
                response, status_code, error_msg = self._retrieve_token_with_retries()
                self._raise_for_status(status_code, error_msg)
                self._update_token_from_response(response, error_msg)
        return self.token

    def _should_refresh_token(self):
        if self.token is None or self.token_expiry_date is None:
            return True

        now = datetime.now(timezone.utc)
        # Check if token has expired incl. buffer
        return self.token_expiry_date - now < timedelta(minutes=60)

    def _calc_token_expiry_date(self, expires_in: str):
        now = datetime.now(timezone.utc)
        # Calculate the token expiry date starting now adding expires in
        self.token_expiry_date = now + timedelta(seconds=int(expires_in))
