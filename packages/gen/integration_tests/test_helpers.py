"""Helper utilities for making integration tests more reliable."""
import time
import inspect
from functools import wraps
from typing import Callable, TypeVar, Any
import logging
import pytest

logger = logging.getLogger(__name__)

T = TypeVar('T')


def retry_on_429_or_503(max_retries: int = 3, initial_delay: float = 2.0, backoff_factor: float = 2.0,
                        skip_on_failure: bool = False):
    """
    Decorator to retry a function when it encounters rate limiting (429) or temporary service errors (503).

    :param max_retries: Maximum number of retry attempts
    :param initial_delay: Initial delay in seconds before first retry
    :param backoff_factor: Multiplier for delay between retries (exponential backoff)
    :param skip_on_failure: If True, skip the test instead of failing when rate limit (429) retries are exhausted
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            delay = initial_delay
            last_exception = None
            was_rate_limited = False

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    error_message = str(e).lower()

                    # Check if it's a retryable error
                    is_rate_limit = '429' in str(e) or 'too many requests' in error_message
                    is_service_unavailable = '503' in str(e) or 'service unavailable' in error_message
                    is_gateway_timeout = '504' in str(e) or 'gateway' in error_message

                    if is_rate_limit:
                        was_rate_limited = True

                    if not (is_rate_limit or is_service_unavailable or is_gateway_timeout):
                        # Not a retryable error, raise immediately
                        raise

                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed with retryable error: {e}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed. Last error: {e}")

            # Skip test if configured and it was a rate limit issue
            if skip_on_failure and was_rate_limited:
                pytest.skip(f"Test skipped after {max_retries + 1} failed attempts due to rate limiting: "
                            f"{last_exception}")

            raise last_exception

        return wrapper
    return decorator

def retry_on_429_or_503_class(max_retries: int = 3, initial_delay: float = 2.0, backoff_factor: float = 2.0,
                               skip_on_failure: bool = False):
    """
    Class decorator to apply retry_on_429_or_503 to all test methods in a class.
    :param max_retries: Maximum number of retry attempts
    :param initial_delay: Initial delay in seconds before first retry
    :param backoff_factor: Multiplier for delay between retries (exponential backoff)
    :param skip_on_failure: If True, skip the test instead of failing when rate limit (429) retries are exhausted
    """
    def class_decorator(cls):
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            if name.startswith('test'):
                decorated = retry_on_429_or_503(
                    max_retries=max_retries,
                    initial_delay=initial_delay,
                    backoff_factor=backoff_factor,
                    skip_on_failure=skip_on_failure
                )(method)
                setattr(cls, name, decorated)
        return cls
    return class_decorator

def with_retry_on_missing_resource(max_retries: int = 3, delay: float = 2.0):
    """
    Decorator to retry a function when it encounters a missing resource error.
    Useful for handling race conditions where resources haven't fully propagated yet.

    :param max_retries: Maximum number of retry attempts
    :param delay: Delay in seconds between retries
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    error_message = str(e).lower()

                    # Check if it's a missing resource error
                    is_not_found = ('not found' in error_message or
                                   '404' in str(e) or
                                   'collection' in error_message and 'not found' in error_message)

                    if not is_not_found:
                        # Not a missing resource error, raise immediately
                        raise

                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed with missing resource: {e}. "
                            f"Waiting {delay}s for resource to be available..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(f"Resource still not found after {max_retries + 1} attempts. Last error: {e}")

            raise last_exception

        return wrapper
    return decorator
