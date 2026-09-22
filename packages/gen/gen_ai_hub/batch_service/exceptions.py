"""
Exceptions for the batch service module.
"""

try:
    import httpx2
except ModuleNotFoundError:
    import httpx as httpx2  # type: ignore[no-redef]
    import warnings
    warnings.warn(
        "httpx is deprecated; install httpx2 instead.",
        DeprecationWarning,
        stacklevel=1,
    )


class BatchServiceError(Exception):
    """
    Raised when the batch service returns an error response.

    Captures the request_id from the error payload for tracing.
    """

    def __init__(
        self,
        request_id: str,
        message: str,
        status_code: int,
        headers: httpx2.Headers,
    ):
        self.request_id = request_id
        self.message = message
        self.status_code = status_code
        self.headers = headers
        super().__init__(message)


__all__ = ["BatchServiceError"]
