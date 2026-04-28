"""
Pytest configuration for integration tests.
Automatically loads environment variables from .env file if present.
"""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


def pytest_configure(config):
    """Load .env file at pytest startup if python-dotenv is available."""
    if load_dotenv is None:
        return
    
    # Look for .env in the project root
    repo_root = Path(__file__).parent.parent
    env_file = repo_root / ".env"
    
    if env_file.exists():
        load_dotenv(env_file)
