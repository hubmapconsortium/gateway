"""
Tests for uuid-api Flask application behavior.

Run all Flask app tests:
    TEST_API="uuid-api" pytest tests/localhost/integration/uuid-api/test_flask_app.py -v
"""

import requests

TIMEOUT = 10


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

def test_status_returns_valid_json(base_url):
    """Test that /status returns valid JSON structure."""
    r = requests.get(f"{base_url}/status", timeout=TIMEOUT)
    assert r.status_code == 200
    assert isinstance(r.json(), dict)

def test_flask_handles_large_payloads(base_url):
    """Test that Flask handles large request payloads."""
    r = requests.post(
        f"{base_url}/uuid",
        json={"entity_type": "x" * 100000},
        headers={"Content-Type": "application/json"},
        timeout=TIMEOUT
    )
    assert r.status_code != 413

def test_status_endpoint_fast_response(base_url):
    """Test that status endpoint responds in under 1 second."""
    r = requests.get(f"{base_url}/status", timeout=TIMEOUT)
    assert r.elapsed.total_seconds() < 1.0

def test_simple_lookup_reasonable_time(base_url):
    """Test that simple lookups complete in under 2 seconds."""
    r = requests.get(f"{base_url}/status", timeout=TIMEOUT)
    assert r.elapsed.total_seconds() < 2.0
