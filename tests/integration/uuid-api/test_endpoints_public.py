"""
Tests for public uuid-api endpoints accessible without authentication.

Auth classification source:
  gateway/api_endpoints.localhost.json, branch karlburke/CaptureAPIUsage

Run all public endpoint tests:
    TEST_API="uuid-api" pytest tests/localhost/integration/uuid-api/ -m "not requires_auth" -v
"""

import requests

TIMEOUT = 10
_ID = "32323232323232323232323232323232"
_HMID = "HBM123.ABCD.456"


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


# ---------------------------------------------------------------------------
# GET - ID parameter, assert 404 or 400 (not 401)
# ---------------------------------------------------------------------------

# gateway api_endpoints.*.json authorization: GET /uuid/<*> auth: false
def test_uuid_lookup(base_url):
    """Test GET /uuid/<id> passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/uuid/{_ID}", timeout=TIMEOUT)
    assert r.status_code == 404
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /hmuuid/<*> auth: false
def test_hmuuid_lookup(base_url):
    """Test GET /hmuuid/<hmid> passes auth gate (expect 404, not 401)."""
    r = requests.get(f"{base_url}/hmuuid/{_HMID}", timeout=TIMEOUT)
    assert r.status_code in [400, 404]
    assert r.status_code != 401

# N.B. GET /<*>/ancestors and POST /uuid both return 401 - moved to protected tests
