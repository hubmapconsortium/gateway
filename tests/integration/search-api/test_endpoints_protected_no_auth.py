"""
Tests for protected search-api endpoints requiring authentication.

Auth classification source:
  gateway/api_endpoints.localhost.json, branch karlburke/CaptureAPIUsage
  aws-api-gateway/api_definitions/search-api-v3-DEV-oas30-apigateway.json

Run all protected endpoint tests:
    TEST_API="search-api" pytest tests/localhost/integration/search-api/ -m "not requires_auth" -v
"""

import requests

TIMEOUT = 10
_INDEX = "test-index"
_ID = "32323232323232323232323232323232"


# ---------------------------------------------------------------------------
# PUT - requires auth
# ---------------------------------------------------------------------------

# gateway api_endpoints.*.json authorization: PUT /reindex/<*> auth: true (read)
def test_reindex_requires_auth(base_url):
    """Test PUT /reindex/<id> returns 401 and not 200 without token."""
    r = requests.put(f"{base_url}/reindex/{_ID}", timeout=TIMEOUT)
    assert r.status_code == 401
    assert r.status_code != 200

# gateway api_endpoints.*.json authorization: PUT /update/<*> auth: true (read)
def test_update_requires_auth(base_url):
    """Test PUT /update/<id> returns 401 and not 200 without token."""
    r = requests.put(
        f"{base_url}/update/{_ID}",
        json={},
        headers={"Content-Type": "application/json"},
        timeout=TIMEOUT
    )
    assert r.status_code == 401
    assert r.status_code != 200

# gateway api_endpoints.*.json authorization: PUT /update/<*>/<*> auth: true (read)
# N.B. multi-parameter endpoints may return 400 before auth check
def test_update_with_index_requires_auth(base_url):
    """Test PUT /update/<id>/<index> returns 401 or 400 and not 200 without token."""
    r = requests.put(
        f"{base_url}/update/{_ID}/{_INDEX}",
        json={},
        headers={"Content-Type": "application/json"},
        timeout=TIMEOUT
    )
    assert r.status_code in [400, 401]
    assert r.status_code != 200

# gateway api_endpoints.*.json authorization: PUT /update/<*>/<*>/<*> auth: true (read)
# N.B. multi-parameter endpoints may return 400 before auth check
def test_update_with_index_and_scope_requires_auth(base_url):
    """Test PUT /update/<id>/<index>/<scope> returns 401 or 400 and not 200 without token."""
    r = requests.put(
        f"{base_url}/update/{_ID}/{_INDEX}/test-scope",
        json={},
        headers={"Content-Type": "application/json"},
        timeout=TIMEOUT
    )
    assert r.status_code in [400, 401]
    assert r.status_code != 200


# ---------------------------------------------------------------------------
# POST - requires auth
# ---------------------------------------------------------------------------

# gateway api_endpoints.*.json authorization: POST /add/<*> auth: true (read)
def test_add_requires_auth(base_url):
    """Test POST /add/<id> returns 401 and not 200 without token."""
    r = requests.post(
        f"{base_url}/add/{_ID}",
        json={},
        headers={"Content-Type": "application/json"},
        timeout=TIMEOUT
    )
    assert r.status_code == 401
    assert r.status_code != 200

# gateway api_endpoints.*.json authorization: POST /add/<*>/<*> auth: true (read)
# N.B. multi-parameter endpoints may return 400 before auth check
def test_add_with_index_requires_auth(base_url):
    """Test POST /add/<id>/<index> returns 401 or 400 and not 200 without token."""
    r = requests.post(
        f"{base_url}/add/{_ID}/{_INDEX}",
        json={},
        headers={"Content-Type": "application/json"},
        timeout=TIMEOUT
    )
    assert r.status_code in [400, 401]
    assert r.status_code != 200

# gateway api_endpoints.*.json authorization: POST /add/<*>/<*>/<*> auth: true (read)
# N.B. multi-parameter endpoints may return 400 before auth check
def test_add_with_index_and_scope_requires_auth(base_url):
    """Test POST /add/<id>/<index>/<scope> returns 401 or 400 and not 200 without token."""
    r = requests.post(
        f"{base_url}/add/{_ID}/{_INDEX}/test-scope",
        json={},
        headers={"Content-Type": "application/json"},
        timeout=TIMEOUT
    )
    assert r.status_code in [400, 401]
    assert r.status_code != 200

# gateway api_endpoints.*.json authorization: POST /clear-docs/<*> auth: true (read)
# N.B. multi-parameter endpoints may return 400 before auth check
def test_clear_docs_requires_auth(base_url):
    """Test POST /clear-docs/<index> returns 401 or 400 and not 200 without token."""
    r = requests.post(
        f"{base_url}/clear-docs/{_INDEX}",
        json={},
        headers={"Content-Type": "application/json"},
        timeout=TIMEOUT
    )
    assert r.status_code in [400, 401]
    assert r.status_code != 200

# gateway api_endpoints.*.json authorization: POST /clear-docs/<*>/<*> auth: true (read)
# N.B. multi-parameter endpoints may return 400 before auth check
def test_clear_docs_with_id_requires_auth(base_url):
    """Test POST /clear-docs/<index>/<id> returns 401 or 400 and not 200 without token."""
    r = requests.post(
        f"{base_url}/clear-docs/{_INDEX}/{_ID}",
        json={},
        headers={"Content-Type": "application/json"},
        timeout=TIMEOUT
    )
    assert r.status_code in [400, 401]
    assert r.status_code != 200

# gateway api_endpoints.*.json authorization: POST /clear-docs/<*>/<*>/<*> auth: true (read)
# N.B. multi-parameter endpoints may return 400 before auth check
def test_clear_docs_with_id_and_scope_requires_auth(base_url):
    """Test POST /clear-docs/<index>/<id>/<scope> returns 401 or 400 and not 200 without token."""
    r = requests.post(
        f"{base_url}/clear-docs/{_INDEX}/{_ID}/test-scope",
        json={},
        headers={"Content-Type": "application/json"},
        timeout=TIMEOUT
    )
    assert r.status_code in [400, 401]
    assert r.status_code != 200
