"""
HTTP mock boundary for tests.

All test HTTP interception goes through HttpMocker.
To migrate to a different mock backend, change only this file.
"""
import respx

from gen_ai_hub.http_types import httpx_Response


class HttpMocker:
    """
    Wraps respx behind a stable interface.

    Usage::

        with HttpMocker() as m:
            m.mock_response("POST", url, status_code=200, json=DATA)
            # ... test code ...

        with HttpMocker() as m:
            m.mock_callback("POST", url, callback=my_fn)
            # ... test code ...
    """

    def __init__(self) -> None:
        self._router = respx.MockRouter(assert_all_called=False)

    def mock_response(
        self,
        method: str,
        url: str,
        *,
        status_code: int,
        json=None,
        content: bytes = None,
        headers: dict = None,
        stream=None,
    ) -> "HttpMocker":
        kwargs = {}
        if json is not None:
            kwargs["json"] = json
        if content is not None:
            kwargs["content"] = content
        if headers is not None:
            kwargs["headers"] = headers
        if stream is not None:
            kwargs["stream"] = stream
        response = httpx_Response(status_code, **kwargs)
        getattr(self._router, method.lower())(url).mock(return_value=response)
        return self

    def mock_callback(self, method: str, url: str, *, callback) -> "HttpMocker":
        getattr(self._router, method.lower())(url).mock(side_effect=callback)
        return self

    def __enter__(self) -> "HttpMocker":
        self._router.__enter__()
        return self

    def __exit__(self, *args) -> None:
        self._router.__exit__(*args)
