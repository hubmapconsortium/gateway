"""
Tests for protected search-api endpoints using a valid bearer token.

Auth classification source:
  gateway/api_endpoints.localhost.json, branch karlburke/CaptureAPIUsage
  aws-api-gateway/api_definitions/search-api-v3-DEV-oas30-apigateway.json

Run all authenticated endpoint tests:
    TEST_API="search-api" SEARCH_API_AUTH_TOKEN="your-token" pytest tests/localhost/integration/search-api/ -v
"""

import pytest
import requests

pytestmark = pytest.mark.requires_auth

TIMEOUT = 10
_INDEX = "test-index"
_ID = "32323232323232323232323232323232"


# ---------------------------------------------------------------------------
# PUT - requires auth
# ---------------------------------------------------------------------------

# gateway api_endpoints.*.json authorization: PUT /reindex/<*> auth: true (read)
def test_reindex_with_auth(base_url, auth_headers):
    """Test PUT /reindex/<id> returns 200 and not 401 with valid token."""
    r = requests.put(f"{base_url}/reindex/{_ID}", headers=auth_headers, timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: PUT /update/<*> auth: true (read)
def test_update_with_auth(base_url, auth_headers):
    """Test PUT /update/<id> returns 200 and not 401 with valid token."""
    r = requests.put(
        f"{base_url}/update/{_ID}",
        json={},
        headers=auth_headers,
        timeout=TIMEOUT
    )
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: PUT /update/<*>/<*> auth: true (read)
def test_update_with_index_with_auth(base_url, auth_headers):
    """Test PUT /update/<id>/<index> returns 200 and not 401 with valid token."""
    r = requests.put(
        f"{base_url}/update/{_ID}/{_INDEX}",
        json={},
        headers=auth_headers,
        timeout=TIMEOUT
    )
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: PUT /update/<*>/<*>/<*> auth: true (read)
def test_update_with_index_and_scope_with_auth(base_url, auth_headers):
    """Test PUT /update/<id>/<index>/<scope> returns 200 and not 401 with valid token."""
    r = requests.put(
        f"{base_url}/update/{_ID}/{_INDEX}/test-scope",
        json={},
        headers=auth_headers,
        timeout=TIMEOUT
    )
    assert r.status_code == 200
    assert r.status_code != 401


# ---------------------------------------------------------------------------
# POST - requires auth
# ---------------------------------------------------------------------------

# gateway api_endpoints.*.json authorization: POST /add/<*> auth: true (read)
def test_add_with_auth(base_url, auth_headers):
    """Test POST /add/<id> returns 200 and not 401 with valid token."""
    r = requests.post(
        f"{base_url}/add/{_ID}",
        json={},
        headers=auth_headers,
        timeout=TIMEOUT
    )
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: POST /add/<*>/<*> auth: true (read)
def test_add_with_index_with_auth(base_url, auth_headers):
    """Test POST /add/<id>/<index> returns 200 and not 401 with valid token."""
    r = requests.post(
        f"{base_url}/add/{_ID}/{_INDEX}",
        json={},
        headers=auth_headers,
        timeout=TIMEOUT
    )
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: POST /add/<*>/<*>/<*> auth: true (read)
def test_add_with_index_and_scope_with_auth(base_url, auth_headers):
    """Test POST /add/<id>/<index>/<scope> returns 200 and not 401 with valid token."""
    r = requests.post(
        f"{base_url}/add/{_ID}/{_INDEX}/test-scope",
        json={},
        headers=auth_headers,
        timeout=TIMEOUT
    )
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: POST /clear-docs/<*> auth: true (read)
def test_clear_docs_with_auth(base_url, auth_headers):
    """Test POST /clear-docs/<index> returns 200 and not 401 with valid token."""
    r = requests.post(
        f"{base_url}/clear-docs/{_INDEX}",
        json={},
        headers=auth_headers,
        timeout=TIMEOUT
    )
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: POST /clear-docs/<*>/<*> auth: true (read)
def test_clear_docs_with_id_with_auth(base_url, auth_headers):
    """Test POST /clear-docs/<index>/<id> returns 200 and not 401 with valid token."""
    r = requests.post(
        f"{base_url}/clear-docs/{_INDEX}/{_ID}",
        json={},
        headers=auth_headers,
        timeout=TIMEOUT
    )
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: POST /clear-docs/<*>/<*>/<*> auth: true (read)
def test_clear_docs_with_id_and_scope_with_auth(base_url, auth_headers):
    """Test POST /clear-docs/<index>/<id>/<scope> returns 200 and not 401 with valid token."""
    r = requests.post(
        f"{base_url}/clear-docs/{_INDEX}/{_ID}/test-scope",
        json={},
        headers=auth_headers,
        timeout=TIMEOUT
    )
    assert r.status_code == 200
    assert r.status_code != 401
