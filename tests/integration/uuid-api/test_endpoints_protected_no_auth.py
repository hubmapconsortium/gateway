"""
Tests for protected uuid-api endpoints requiring authentication.

Auth classification source:
  gateway/api_endpoints.localhost.json, branch karlburke/CaptureAPIUsage

Run all protected endpoint tests:
    TEST_API="uuid-api" pytest tests/localhost/integration/uuid-api/ -m "not requires_auth" -v
"""

import requests

TIMEOUT = 10
_ID = "32323232323232323232323232323232"
_HMID = "HBM123.ABCD.456"


# ---------------------------------------------------------------------------
# GET - requires auth
# ---------------------------------------------------------------------------

# gateway api_endpoints.*.json authorization: GET /uuid/<*>/exists auth: true (read)
def test_uuid_exists_requires_auth(base_url):
    """Test GET /uuid/<id>/exists returns 401 and not 200 without token."""
    r = requests.get(f"{base_url}/uuid/{_ID}/exists", timeout=TIMEOUT)
    assert r.status_code == 401
    assert r.status_code != 200

# gateway api_endpoints.*.json authorization: GET /hmuuid/<*>/exists auth: true (read)
def test_hmuuid_exists_requires_auth(base_url):
    """Test GET /hmuuid/<hmid>/exists returns 401 and not 200 without token."""
    r = requests.get(f"{base_url}/hmuuid/{_HMID}/exists", timeout=TIMEOUT)
    assert r.status_code == 401
    assert r.status_code != 200

# gateway api_endpoints.*.json authorization: GET /file-id/<*> auth: true (read)
def test_file_id_requires_auth(base_url):
    """Test GET /file-id/<id> returns 401 and not 200 without token."""
    r = requests.get(f"{base_url}/file-id/{_ID}", timeout=TIMEOUT)
    assert r.status_code == 401
    assert r.status_code != 200

# gateway api_endpoints.*.json authorization: GET /<*>/files auth: true (read)
def test_files_requires_auth(base_url):
    """Test GET /<id>/files returns 401 and not 200 without token."""
    r = requests.get(f"{base_url}/{_ID}/files", timeout=TIMEOUT)
    assert r.status_code == 401
    assert r.status_code != 200


# gateway api_endpoints.*.json authorization: GET /<*>/ancestors auth: true (read)
def test_ancestors_requires_auth(base_url):
    """Test GET /<id>/ancestors returns 401 and not 200 without token."""
    r = requests.get(f"{base_url}/{_ID}/ancestors", timeout=TIMEOUT)
    assert r.status_code == 401
    assert r.status_code != 200

# gateway api_endpoints.*.json authorization: POST /uuid auth: true (read)
def test_uuid_post_requires_auth(base_url):
    """Test POST /uuid returns 401 and not 200 without token."""
    r = requests.post(
        f"{base_url}/uuid",
        json={},
        headers={"Content-Type": "application/json"},
        timeout=TIMEOUT
    )
    assert r.status_code == 401
    assert r.status_code != 200


# ---------------------------------------------------------------------------
# POST - requires auth
# ---------------------------------------------------------------------------

# gateway api_endpoints.*.json authorization: POST /hmuuid auth: true (read)
def test_hmuuid_post_requires_auth(base_url):
    """Test POST /hmuuid returns 401 and not 200 without token."""
    r = requests.post(
        f"{base_url}/hmuuid",
        json={},
        headers={"Content-Type": "application/json"},
        timeout=TIMEOUT
    )
    assert r.status_code == 401
    assert r.status_code != 200
