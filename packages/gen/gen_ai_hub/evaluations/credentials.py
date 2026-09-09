from __future__ import annotations

from typing import Dict, Final, List

from ai_core_sdk.credentials import (
    CORE_CREDENTIAL_VALUES,
    CredentialsValue,
    Service,
    Source,
    VCAPEnvironment,
    extract_credentials as _extract_core_credentials,
    fetch_credentials as _fetch_core_credentials,
    get_nested_value,
    init_conf,
    resolve_credentials as _resolve_core_credentials,
    resolve_resource_group,
    validate_credentials,
)
from ai_core_sdk.helpers import get_home

# Re-exported for backward compatibility: these are generic and fully reused from ai_core_sdk.credentials.
__all__ = [
    "CredentialsValue",
    "Service",
    "Source",
    "VCAPEnvironment",
    "EVAL_CREDENTIAL_VALUES",
    "extract_credentials",
    "fetch_credentials",
    "get_home",
    "get_nested_value",
    "init_conf",
    "resolve_credentials",
    "resolve_resource_group",
    "validate_credentials",
]

# Extends the core credential values with evaluation-specific ones.
# Currently supporting only the AWS creds, would need to extend to other hyperscalers in future.
EVAL_CREDENTIAL_VALUES: Final[List[CredentialsValue]] = CORE_CREDENTIAL_VALUES + [
    CredentialsValue(name='aws_access_key_id'),
    CredentialsValue(name='aws_secret_access_key'),
    CredentialsValue(name='orchestration_url'),
    CredentialsValue(name='input_object_store_secret_name'),
]


def extract_credentials(source: Source, exclude: List[str] = None) -> Dict[str, str]:
    """Extract all evaluation credentials from a source."""
    return _extract_core_credentials(source, credential_values=EVAL_CREDENTIAL_VALUES, exclude=exclude)


def resolve_credentials(sources: List[Source]) -> Dict[str, str]:
    """Extract evaluation credentials from the first source that has any defined."""
    return _resolve_core_credentials(sources, credential_values=EVAL_CREDENTIAL_VALUES)


def fetch_credentials(profile: str = None, **kwargs) -> Dict[str, str]:
    """
    Fetch evaluation credentials from a single source based on precedence.

    Precedence order: kwargs > environment variables > AICORE_SERVICE_KEY > config file > VCAP service
    (see ai_core_sdk.credentials.fetch_credentials for the full behavior).
    """
    return _fetch_core_credentials(profile=profile, credential_values=EVAL_CREDENTIAL_VALUES, **kwargs)
