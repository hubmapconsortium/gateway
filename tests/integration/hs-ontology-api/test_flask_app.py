"""
Tests for hs-ontology-api Flask application behavior.

These tests verify Flask-specific functionality including error handling,
404 responses for undefined routes, and application-level logic.

Run all Flask app tests:
    TEST_API="hs-ontology-api" pytest tests/localhost/integration/hs-ontology-api/test_flask_app.py -v
"""

import requests

TIMEOUT = 10


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

def test_undefined_endpoint_returns_404(base_url):
    """Test that undefined endpoints return 404 from Flask."""
    r = requests.get(f"{base_url}/this-endpoint-does-not-exist", timeout=TIMEOUT)
    assert r.status_code == 404

def test_undefined_post_endpoint_returns_404(base_url):
    """Test that undefined POST endpoints return 404."""
    r = requests.post(
        f"{base_url}/undefined-post-endpoint",
        json={"test": "data"},
        headers={"Content-Type": "application/json"},
        timeout=TIMEOUT
    )
    assert r.status_code == 404

def test_undefined_put_endpoint_returns_404(base_url):
    """Test that undefined PUT endpoints return 404."""
    r = requests.put(
        f"{base_url}/undefined-put-endpoint",
        json={"test": "data"},
        headers={"Content-Type": "application/json"},
        timeout=TIMEOUT
    )
    assert r.status_code == 404

def test_undefined_delete_endpoint_returns_404(base_url):
    """Test that undefined DELETE endpoints return 404."""
    r = requests.delete(f"{base_url}/undefined-delete-endpoint", timeout=TIMEOUT)
    assert r.status_code == 404

def test_invalid_identifier_handled_gracefully(base_url):
    """Test that invalid identifiers are handled with proper error codes."""
    r = requests.get(f"{base_url}/concepts/not-a-valid-concept-id/codes", timeout=TIMEOUT)
    assert r.status_code in [400, 404]


# ---------------------------------------------------------------------------
# Response structure
# ---------------------------------------------------------------------------

def test_status_returns_valid_json(base_url):
    """Test that /status returns valid JSON structure."""
    r = requests.get(f"{base_url}/status", timeout=TIMEOUT)
    assert r.status_code == 200
    assert isinstance(r.json(), dict)

def test_property_types_returns_list_or_dict(base_url):
    """Test that /property-types returns proper data structure."""
    r = requests.get(f"{base_url}/property-types", timeout=TIMEOUT)
    assert r.status_code == 200
    assert isinstance(r.json(), (list, dict))

def test_flask_handles_large_payloads(base_url):
    """Test that Flask handles large request payloads."""
    r = requests.get(
        f"{base_url}/valueset",
        params={"parent_sab": "x" * 10000, "child_sabs": "x", "parent_code": "x"},
        timeout=TIMEOUT
    )
    assert r.status_code != 413


# ---------------------------------------------------------------------------
# Performance
# ---------------------------------------------------------------------------

def test_status_endpoint_fast_response(base_url):
    """Test that status endpoint responds in under 1 second."""
    r = requests.get(f"{base_url}/status", timeout=TIMEOUT)
    assert r.elapsed.total_seconds() < 1.0

def test_simple_lookup_reasonable_time(base_url):
    """Test that simple lookups complete in under 2 seconds."""
    r = requests.get(f"{base_url}/property-types", timeout=TIMEOUT)
    assert r.elapsed.total_seconds() < 2.0
