"""
Tests for public antibody-api endpoints accessible without authentication.

Auth classification source:
  gateway/api_endpoints.localhost.json, branch karlburke/CaptureAPIUsage

All antibody-api endpoints are public — no authorizer is configured.

Run all public endpoint tests:
    TEST_API="antibody-api" pytest tests/localhost/integration/antibody-api/ -v
"""

import requests

TIMEOUT = 10

# TODO: implement tests
