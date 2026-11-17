"""
Tests for protected uuid-api endpoints using a valid bearer token.

Auth classification source:
  gateway/api_endpoints.localhost.json, branch karlburke/CaptureAPIUsage

Run all authenticated endpoint tests:
    TEST_API="uuid-api" UUID_API_AUTH_TOKEN="your-token" pytest tests/localhost/integration/uuid-api/ -v
"""

import pytest
import requests

pytestmark = pytest.mark.requires_auth

TIMEOUT = 10
_ID = "32323232323232323232323232323232"
_HMID = "HBM123.ABCD.456"


# ---------------------------------------------------------------------------
# GET - requires auth
# ---------------------------------------------------------------------------

# gateway api_endpoints.*.json authorization: GET /uuid/<*>/exists auth: true (read)
def test_uuid_exists_with_auth(base_url, auth_headers):
    """Test GET /uuid/<id>/exists returns 200 and not 401 with valid token."""
    r = requests.get(f"{base_url}/uuid/{_ID}/exists", headers=auth_headers, timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /hmuuid/<*>/exists auth: true (read)
def test_hmuuid_exists_with_auth(base_url, auth_headers):
    """Test GET /hmuuid/<hmid>/exists returns 200 and not 401 with valid token."""
    r = requests.get(f"{base_url}/hmuuid/{_HMID}/exists", headers=auth_headers, timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /file-id/<*> auth: true (read)
def test_file_id_with_auth(base_url, auth_headers):
    """Test GET /file-id/<id> returns 200 and not 401 with valid token."""
    r = requests.get(f"{base_url}/file-id/{_ID}", headers=auth_headers, timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /<*>/files auth: true (read)
def test_files_with_auth(base_url, auth_headers):
    """Test GET /<id>/files returns 200 and not 401 with valid token."""
    r = requests.get(f"{base_url}/{_ID}/files", headers=auth_headers, timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401


# ---------------------------------------------------------------------------
# POST - requires auth
# ---------------------------------------------------------------------------

# gateway api_endpoints.*.json authorization: POST /hmuuid auth: true (read)
def test_hmuuid_post_with_auth(base_url, auth_headers):
    """Test POST /hmuuid returns 200 and not 401 with valid token."""
    r = requests.post(
        f"{base_url}/hmuuid",
        json={},
        headers=auth_headers,
        timeout=TIMEOUT
    )
    assert r.status_code == 200
    assert r.status_code != 401
