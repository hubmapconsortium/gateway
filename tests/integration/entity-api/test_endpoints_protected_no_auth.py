"""
Tests for protected entity-api endpoints requiring authentication.

Auth classification source:
  gateway/api_endpoints.localhost.json, branch karlburke/CaptureAPIUsage

These tests call entity-api endpoints directly and verify they require
proper authentication. No knowledge of hubmap-auth /api_auth internals.

Run all protected endpoint tests:
    pytest test_endpoints_protected_no_auth.py -v

Run a subset by name pattern:
    pytest test_endpoints_protected_no_auth.py -k "datasets" -v
"""

import requests

TIMEOUT = 10


# ---------------------------------------------------------------------------
# GET
# ---------------------------------------------------------------------------

# gateway api_endpoints.*.json authorization: GET /usergroups auth: true
# @app.route('/usergroups', methods = ['GET'])
def test_usergroups_requires_auth(base_url):
    """Test GET /usergroups returns 401 and not 200 without token."""
    r = requests.get(f"{base_url}/usergroups", timeout=TIMEOUT)
    assert r.status_code == 401
    assert r.status_code != 200

# gateway api_endpoints.*.json authorization: GET /descendants/<*> auth: true
# @app.route('/descendants/<id>', methods = ['GET'])
def test_descendants_requires_auth(base_url):
    """Test GET /descendants/<id> returns 401 and not 200 without token."""
    r = requests.get(f"{base_url}/descendants/test-id", timeout=TIMEOUT)
    assert r.status_code == 401
    assert r.status_code != 200

# gateway api_endpoints.*.json authorization: GET /children/<*> auth: true
# @app.route('/children/<id>', methods = ['GET'])
def test_children_requires_auth(base_url):
    """Test GET /children/<id> returns 401 and not 200 without token."""
    r = requests.get(f"{base_url}/children/test-id", timeout=TIMEOUT)
    assert r.status_code == 401
    assert r.status_code != 200

# gateway api_endpoints.*.json authorization: GET /datasets/unpublished auth: true
# @app.route('/datasets/unpublished', methods=['GET'])
def test_datasets_unpublished_requires_auth(base_url):
    """Test GET /datasets/unpublished returns 401 and not 200 without token."""
    r = requests.get(f"{base_url}/datasets/unpublished", timeout=TIMEOUT)
    assert r.status_code == 401
    assert r.status_code != 200

# gateway api_endpoints.*.json authorization: GET /previous_revisions/<*> auth: true
# @app.route('/previous_revisions/<id>', methods = ['GET'])
def test_previous_revisions_requires_auth(base_url):
    """Test GET /previous_revisions/<id> returns 401 and not 200 without token."""
    r = requests.get(f"{base_url}/previous_revisions/test-id", timeout=TIMEOUT)
    assert r.status_code == 401
    assert r.status_code != 200

# gateway api_endpoints.*.json authorization: GET /next_revisions/<*> auth: true
# @app.route('/next_revisions/<id>', methods = ['GET'])
def test_next_revisions_requires_auth(base_url):
    """Test GET /next_revisions/<id> returns 401 and not 200 without token."""
    r = requests.get(f"{base_url}/next_revisions/test-id", timeout=TIMEOUT)
    assert r.status_code == 401
    assert r.status_code != 200


# ---------------------------------------------------------------------------
# POST
# ---------------------------------------------------------------------------

# gateway api_endpoints.*.json authorization: POST /entities/<*> auth: true
# @app.route('/entities/<entity_type>', methods = ['POST'])
def test_entities_create_requires_auth(base_url):
    """Test POST /entities/<type> returns 401 and not 200 without token."""
    r = requests.post(
        f"{base_url}/entities/sample",
        json={"direct_ancestor_uuid": "test-uuid"},
        headers={"Content-Type": "application/json"},
        timeout=TIMEOUT
    )
    assert r.status_code == 401
    assert r.status_code != 200

# gateway api_endpoints.*.json authorization: POST /entities/multiple-samples/<*> auth: true
# @app.route('/entities/multiple-samples/<count>', methods = ['POST'])
def test_entities_multiple_samples_requires_auth(base_url):
    """Test POST /entities/multiple-samples/<count> returns 401 and not 200 without token."""
    r = requests.post(
        f"{base_url}/entities/multiple-samples/5",
        json={"direct_ancestor_uuid": "test-uuid"},
        headers={"Content-Type": "application/json"},
        timeout=TIMEOUT
    )
    assert r.status_code == 401
    assert r.status_code != 200

# gateway api_endpoints.*.json authorization: POST /datasets/components auth: true
# @app.route('/datasets/components', methods=['POST'])
def test_datasets_components_requires_auth(base_url):
    """Test POST /datasets/components returns 401 and not 200 without token."""
    r = requests.post(
        f"{base_url}/datasets/components",
        json={"test": "data"},
        headers={"Content-Type": "application/json"},
        timeout=TIMEOUT
    )
    assert r.status_code == 401
    assert r.status_code != 200


# ---------------------------------------------------------------------------
# PUT
# ---------------------------------------------------------------------------

# gateway api_endpoints.*.json authorization: PUT /entities/<*> auth: true
# @app.route('/entities/<id>', methods = ['PUT'])
def test_entities_update_requires_auth(base_url):
    """Test PUT /entities/<id> returns 401 and not 200 without token."""
    r = requests.put(
        f"{base_url}/entities/test-uuid",
        json={"description": "updated"},
        headers={"Content-Type": "application/json"},
        timeout=TIMEOUT
    )
    assert r.status_code == 401
    assert r.status_code != 200

# gateway api_endpoints.*.json authorization: PUT /datasets/<*>/retract auth: true
# @app.route('/datasets/<id>/retract', methods=['PUT'])
def test_datasets_retract_requires_auth(base_url):
    """Test PUT /datasets/<id>/retract returns 401 and not 200 without token."""
    r = requests.put(
        f"{base_url}/datasets/test-id/retract",
        json={"retraction_reason": "test reason"},
        headers={"Content-Type": "application/json"},
        timeout=TIMEOUT
    )
    assert r.status_code == 401
    assert r.status_code != 200


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------

# gateway api_endpoints.*.json authorization: DELETE /flush-cache/<*> auth: true
# @app.route('/flush-cache/<id>', methods = ['DELETE'])
def test_flush_cache_requires_auth(base_url):
    """Test DELETE /flush-cache/<id> returns 401 and not 200 without token."""
    r = requests.delete(f"{base_url}/flush-cache/test-id", timeout=TIMEOUT)
    assert r.status_code == 401
    assert r.status_code != 200

# gateway api_endpoints.*.json authorization: DELETE /flush-all-cache auth: true
# @app.route('/flush-all-cache', methods = ['DELETE'])
def test_flush_all_cache_requires_auth(base_url):
    """Test DELETE /flush-all-cache returns 401 and not 200 without token."""
    r = requests.delete(f"{base_url}/flush-all-cache", timeout=TIMEOUT)
    assert r.status_code == 401
    assert r.status_code != 200
