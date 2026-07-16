"""
Shared pytest fixtures for HuBMAP API endpoint tests.

Configuration is loaded from test_config.yaml. The target API is selected
by the TEST_API environment variable (defaults to "entity-api"):

    TEST_API="ingest-api" pytest ...
    TEST_API="entity-api" ENTITY_API_AUTH_TOKEN="your-token" pytest ...

Fixtures provided:
    base_url   - verified-reachable base URL for the target API
    fake_uuid  - well-formed UUID known not to exist in the database
    auth_token - validated bearer token (auth tests only)
    auth_headers - Authorization + Content-Type headers (auth tests only)
"""

import os
import pytest
import requests
import yaml
from pathlib import Path
from requests.exceptions import ConnectionError as RequestsConnectionError

_CONFIG_FILE = Path(__file__).parent / "test_config.yaml"
_DEFAULT_API = "entity-api"


def _load_api_config() -> dict:
    """Load config for the API named by TEST_API, defaulting to entity-api."""
    api_name = os.environ.get("TEST_API", _DEFAULT_API)
    with open(_CONFIG_FILE) as f:
        config = yaml.safe_load(f)
    if api_name not in config:
        available = ", ".join(config.keys())
        raise RuntimeError(
            f"TEST_API=\"{api_name}\" not found in {_CONFIG_FILE.name}. "
            f"Available APIs: {available}"
        )
    return config[api_name]


_API_CONFIG = _load_api_config()
_BASE_URL = _API_CONFIG["base_url"]
_TIMEOUT = 10


def _check_connectivity(url: str) -> None:
    """Verify the API is reachable and /status returns 200."""
    try:
        response = requests.get(f"{url}/status", timeout=_TIMEOUT)
        if response.status_code != 200:
            pytest.fail(
                f"API not responding: /status returned {response.status_code}"
            )
    except RequestsConnectionError:
        pytest.fail(
            f"Cannot connect to API at {url}. "
            "Ensure containers are running:\n"
            "  cd gateway && ./docker-localhost.sh start\n"
            "  cd entity-api/docker && ./docker-localhost.sh start"
        )


@pytest.fixture(scope="module")
def base_url():
    """Verify connectivity once per module, then provide BASE_URL to tests."""
    _check_connectivity(_BASE_URL)
    return _BASE_URL


@pytest.fixture(scope="module")
def fake_uuid():
    """Return a well-formed UUID known not to exist in the database.

    Public endpoint tests use this to confirm an auth gate passes (expecting
    404 from business logic, not 401 from the auth gate).
    """
    return _API_CONFIG["fake_uuid"]


@pytest.fixture(scope="module")
def auth_token():
    """Verify ENTITY_API_AUTH_TOKEN is set and connectivity is good, then provide token."""
    env_var = _API_CONFIG["auth_token_env"]
    token = os.environ.get(env_var, "")
    if not token:
        pytest.fail(
            f"{env_var} is not set. "
            "Pass a valid Globus bearer token on the command line:\n"
            f'  {env_var}="your-token-here" pytest ...'
        )
    _check_connectivity(_BASE_URL)
    return token


@pytest.fixture
def auth_headers(auth_token):
    """Return Authorization and Content-Type headers for authenticated requests."""
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
