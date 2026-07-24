"""
Tests for protected ingest-api endpoints using a valid bearer token.

Auth classification source:
  gateway/api_endpoints.localhost.json, branch karlburke/CaptureAPIUsage

Run all authenticated endpoint tests:
    TEST_API="ingest-api" INGEST_API_AUTH_TOKEN="your-token" pytest tests/localhost/integration/ingest-api/ -v
"""

import pytest
import requests

pytestmark = pytest.mark.requires_auth

TIMEOUT = 10

# TODO: implement tests
