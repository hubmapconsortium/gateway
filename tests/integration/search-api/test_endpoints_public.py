"""
Tests for public search-api endpoints accessible without authentication.

Auth classification source:
  gateway/api_endpoints.localhost.json, branch karlburke/CaptureAPIUsage
  aws-api-gateway/api_definitions/search-api-v3-DEV-oas30-apigateway.json

Run all public endpoint tests:
    TEST_API="search-api" pytest tests/localhost/integration/search-api/ -m "not requires_auth" -v
"""

import requests

TIMEOUT = 10
_INDEX = "test-index"
_ID = "32323232323232323232323232323232"


# ---------------------------------------------------------------------------
# GET - no parameter, assert 200
# ---------------------------------------------------------------------------

# gateway api_endpoints.*.json authorization: GET / auth: false
def test_root_endpoint(base_url):
    """Test GET / is publicly accessible."""
    r = requests.get(f"{base_url}/", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /status auth: false
def test_status_endpoint(base_url):
    """Test GET /status is publicly accessible."""
    r = requests.get(f"{base_url}/status", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401
    assert isinstance(r.json(), dict)

# gateway api_endpoints.*.json authorization: GET /indices auth: false
def test_indices(base_url):
    """Test GET /indices is publicly accessible."""
    r = requests.get(f"{base_url}/indices", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /mapping auth: false
def test_mapping(base_url):
    """Test GET /mapping is publicly accessible."""
    r = requests.get(f"{base_url}/mapping", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /attribute-values auth: false
# N.B. requires query parameters - returns 400 without them
def test_attribute_values(base_url):
    """Test GET /attribute-values is publicly accessible (requires params, expect 400 without them)."""
    r = requests.get(f"{base_url}/attribute-values", timeout=TIMEOUT)
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /reindex-status auth: false
# N.B. may return 500 if Redis is unavailable in local dev environment
def test_reindex_status(base_url):
    """Test GET /reindex-status is publicly accessible (may return 500 if Redis unavailable)."""
    r = requests.get(f"{base_url}/reindex-status", timeout=TIMEOUT)
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: POST /search auth: false
# N.B. GET /search returns 405 locally - only POST is supported
def test_search_post_public(base_url):
    """Test POST /search is publicly accessible."""
    r = requests.post(
        f"{base_url}/search",
        json={},
        headers={"Content-Type": "application/json"},
        timeout=TIMEOUT
    )
    assert r.status_code != 401


# ---------------------------------------------------------------------------
# GET - index parameter, assert not 401
# ---------------------------------------------------------------------------

# gateway api_endpoints.*.json authorization: GET /<*>/search auth: false
# N.B. GET /<index>/search returns 405 locally - only POST is supported
def test_index_search_get(base_url):
    """Test GET /<index>/search passes auth gate (expect 405, not 401)."""
    r = requests.get(f"{base_url}/{_INDEX}/search", timeout=TIMEOUT)
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /<*>/mapping auth: false
def test_index_mapping(base_url):
    """Test GET /<index>/mapping passes auth gate (expect 404 or 400, not 401)."""
    r = requests.get(f"{base_url}/{_INDEX}/mapping", timeout=TIMEOUT)
    assert r.status_code in [400, 404]
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /<*>/attribute-values auth: false
def test_index_attribute_values(base_url):
    """Test GET /<index>/attribute-values passes auth gate (expect 404 or 400, not 401)."""
    r = requests.get(f"{base_url}/{_INDEX}/attribute-values", timeout=TIMEOUT)
    assert r.status_code in [400, 404]
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /reindex-status/<*> auth: false
# N.B. may return 500 if Redis is unavailable in local dev environment
def test_reindex_status_by_id(base_url):
    """Test GET /reindex-status/<id> passes auth gate (may return 500 if Redis unavailable)."""
    r = requests.get(f"{base_url}/reindex-status/{_ID}", timeout=TIMEOUT)
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /param-search/<*> auth: false
def test_param_search(base_url):
    """Test GET /param-search/<entity_type> passes auth gate (expect 404 or 400, not 401)."""
    r = requests.get(f"{base_url}/param-search/Dataset", timeout=TIMEOUT)
    assert r.status_code in [400, 404]
    assert r.status_code != 401


# ---------------------------------------------------------------------------
# POST - no parameter, assert not 401
# ---------------------------------------------------------------------------

# gateway api_endpoints.*.json authorization: POST /mget auth: false
def test_mget_post(base_url):
    """Test POST /mget is publicly accessible."""
    r = requests.post(
        f"{base_url}/mget",
        json={},
        headers={"Content-Type": "application/json"},
        timeout=TIMEOUT
    )
    assert r.status_code != 401


# ---------------------------------------------------------------------------
# POST - index parameter, assert not 401
# ---------------------------------------------------------------------------

# gateway api_endpoints.*.json authorization: POST /<*>/search auth: false
def test_index_search_post(base_url):
    """Test POST /<index>/search passes auth gate (expect 404 or 400, not 401)."""
    r = requests.post(
        f"{base_url}/{_INDEX}/search",
        json={},
        headers={"Content-Type": "application/json"},
        timeout=TIMEOUT
    )
    assert r.status_code in [400, 404]
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: POST /<*>/mget auth: false
def test_index_mget_post(base_url):
    """Test POST /<index>/mget passes auth gate (expect 404 or 400, not 401)."""
    r = requests.post(
        f"{base_url}/{_INDEX}/mget",
        json={},
        headers={"Content-Type": "application/json"},
        timeout=TIMEOUT
    )
    assert r.status_code in [400, 404]
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: POST /<*>/scroll-search auth: false
def test_index_scroll_search_post(base_url):
    """Test POST /<index>/scroll-search passes auth gate (expect 404 or 400, not 401)."""
    r = requests.post(
        f"{base_url}/{_INDEX}/scroll-search",
        json={},
        headers={"Content-Type": "application/json"},
        timeout=TIMEOUT
    )
    assert r.status_code in [400, 404]
    assert r.status_code != 401
