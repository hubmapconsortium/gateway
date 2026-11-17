"""
Tests for protected hs-ontology-api endpoints using a valid bearer token.

Auth classification source:
  gateway/api_endpoints.localhost.json, branch karlburke/CaptureAPIUsage

Note: all hs-ontology-api endpoints are currently public. This file is a
placeholder for any protected endpoints added in future.

Run all authenticated endpoint tests:
    TEST_API="hs-ontology-api" HS_ONTOLOGY_API_AUTH_TOKEN="your-token" pytest tests/localhost/integration/hs-ontology-api/ -v
"""

import pytest
import requests

pytestmark = pytest.mark.requires_auth

TIMEOUT = 10

# TODO: implement tests if protected endpoints are added
