import logging
import os

from ai_api_client_sdk.helpers.constants import DEBUG_ENV_VAR_NAME

DEFAULT_LOG_LEVEL = logging.INFO
LOGGER_NAME = "ai-api-client-sdk"

def get_logger():
    return logging.getLogger(get_logger_name())

def get_logger_name():
    return LOGGER_NAME

def set_log_level(logger: logging.Logger):
    debug = os.getenv(DEBUG_ENV_VAR_NAME) is not None and os.getenv(DEBUG_ENV_VAR_NAME).lower() == 'true'
    logger.setLevel(logging.DEBUG if debug else DEFAULT_LOG_LEVEL)
