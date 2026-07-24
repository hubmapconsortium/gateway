"""
Tests for protected entity-api endpoints using a valid bearer token.

Auth classification source:
  gateway/api_endpoints.localhost.json, branch karlburke/CaptureAPIUsage

These tests verify that properly authenticated requests are accepted.
Requires a valid Globus bearer token passed on the command line:

    ENTITY_API_AUTH_TOKEN="your-token-here" pytest test_endpoints_protected_auth.py -v

Run a subset by name pattern:
    ENTITY_API_AUTH_TOKEN="your-token-here" pytest test_endpoints_protected_auth.py -k "datasets" -v
"""

import pytest
import requests

pytestmark = pytest.mark.requires_auth

TIMEOUT = 10


# ---------------------------------------------------------------------------
# GET
# ---------------------------------------------------------------------------

# gateway api_endpoints.*.json authorization: GET /usergroups auth: true
# @app.route('/usergroups', methods = ['GET'])
def test_usergroups_with_auth(base_url, auth_headers):
    """Test GET /usergroups returns 200 and not 401 with valid token."""
    r = requests.get(f"{base_url}/usergroups", headers=auth_headers, timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /descendants/<*> auth: true
# @app.route('/descendants/<id>', methods = ['GET'])
def test_descendants_with_auth(base_url, auth_headers):
    """Test GET /descendants/<id> returns 200 and not 401 with valid token."""
    r = requests.get(f"{base_url}/descendants/test-id", headers=auth_headers, timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /children/<*> auth: true
# @app.route('/children/<id>', methods = ['GET'])
def test_children_with_auth(base_url, auth_headers):
    """Test GET /children/<id> returns 200 and not 401 with valid token."""
    r = requests.get(f"{base_url}/children/test-id", headers=auth_headers, timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /datasets/unpublished auth: true
# @app.route('/datasets/unpublished', methods=['GET'])
def test_datasets_unpublished_with_auth(base_url, auth_headers):
    """Test GET /datasets/unpublished returns 200 and not 401 with valid token."""
    r = requests.get(f"{base_url}/datasets/unpublished", headers=auth_headers, timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /previous_revisions/<*> auth: true
# @app.route('/previous_revisions/<id>', methods = ['GET'])
def test_previous_revisions_with_auth(base_url, auth_headers):
    """Test GET /previous_revisions/<id> returns 200 and not 401 with valid token."""
    r = requests.get(f"{base_url}/previous_revisions/test-id", headers=auth_headers, timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: GET /next_revisions/<*> auth: true
# @app.route('/next_revisions/<id>', methods = ['GET'])
def test_next_revisions_with_auth(base_url, auth_headers):
    """Test GET /next_revisions/<id> returns 200 and not 401 with valid token."""
    r = requests.get(f"{base_url}/next_revisions/test-id", headers=auth_headers, timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401


# ---------------------------------------------------------------------------
# POST
# ---------------------------------------------------------------------------

# gateway api_endpoints.*.json authorization: POST /entities/<*> auth: true
# @app.route('/entities/<entity_type>', methods = ['POST'])
def test_entities_create_with_auth(base_url, auth_headers):
    """Test POST /entities/<type> returns 200 and not 401 with valid token."""
    r = requests.post(
        f"{base_url}/entities/sample",
        json={"direct_ancestor_uuid": "test-uuid"},
        headers=auth_headers,
        timeout=TIMEOUT
    )
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: POST /entities/multiple-samples/<*> auth: true
# @app.route('/entities/multiple-samples/<count>', methods = ['POST'])
def test_entities_multiple_samples_with_auth(base_url, auth_headers):
    """Test POST /entities/multiple-samples/<count> returns 200 and not 401 with valid token."""
    r = requests.post(
        f"{base_url}/entities/multiple-samples/5",
        json={"direct_ancestor_uuid": "test-uuid"},
        headers=auth_headers,
        timeout=TIMEOUT
    )
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: POST /datasets/components auth: true
# @app.route('/datasets/components', methods=['POST'])
def test_datasets_components_with_auth(base_url, auth_headers):
    """Test POST /datasets/components returns 200 and not 401 with valid token."""
    r = requests.post(
        f"{base_url}/datasets/components",
        json={"test": "data"},
        headers=auth_headers,
        timeout=TIMEOUT
    )
    assert r.status_code == 200
    assert r.status_code != 401


# ---------------------------------------------------------------------------
# PUT
# ---------------------------------------------------------------------------

# gateway api_endpoints.*.json authorization: PUT /entities/<*> auth: true
# @app.route('/entities/<id>', methods = ['PUT'])
def test_entities_update_with_auth(base_url, auth_headers):
    """Test PUT /entities/<id> returns 200 and not 401 with valid token."""
    r = requests.put(
        f"{base_url}/entities/test-uuid",
        json={"description": "updated"},
        headers=auth_headers,
        timeout=TIMEOUT
    )
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: PUT /datasets/<*>/retract auth: true
# @app.route('/datasets/<id>/retract', methods=['PUT'])
def test_datasets_retract_with_auth(base_url, auth_headers):
    """Test PUT /datasets/<id>/retract returns 200 and not 401 with valid token."""
    r = requests.put(
        f"{base_url}/datasets/test-id/retract",
        json={"retraction_reason": "test reason"},
        headers=auth_headers,
        timeout=TIMEOUT
    )
    assert r.status_code == 200
    assert r.status_code != 401


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------

# gateway api_endpoints.*.json authorization: DELETE /flush-cache/<*> auth: true
# @app.route('/flush-cache/<id>', methods = ['DELETE'])
def test_flush_cache_with_auth(base_url, auth_headers):
    """Test DELETE /flush-cache/<id> returns 200 and not 401 with valid token."""
    r = requests.delete(f"{base_url}/flush-cache/test-id", headers=auth_headers, timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401

# gateway api_endpoints.*.json authorization: DELETE /flush-all-cache auth: true
# @app.route('/flush-all-cache', methods = ['DELETE'])
def test_flush_all_cache_with_auth(base_url, auth_headers):
    """Test DELETE /flush-all-cache returns 200 and not 401 with valid token."""
    r = requests.delete(f"{base_url}/flush-all-cache", headers=auth_headers, timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.status_code != 401
