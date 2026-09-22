"""
Shared SSL context factory for httpx2 clients.

httpx2 defaults to the OS trust store (truststore). This module preserves
the pre-migration behaviour of using certifi's CA bundle so existing
deployments are not affected. Switch callers to verify=True to adopt the
httpx2 default when ready.
"""
import ssl
import certifi


def default_ssl_context() -> ssl.SSLContext:
    """Return an SSL context backed by certifi's CA bundle."""
    return ssl.create_default_context(cafile=certifi.where())
