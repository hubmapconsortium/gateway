"""
Tests for CORS (Cross-Origin Resource Sharing) configuration in entity-api.

CORS headers enable web browsers to make requests to the API from
different origins. These tests verify proper CORS configuration in nginx.

Run all CORS tests:
    pytest test_cors.py -v
"""

import requests

TIMEOUT = 10


# ---------------------------------------------------------------------------
# CORS response headers
# ---------------------------------------------------------------------------

def test_cors_allow_origin_header(base_url):
    """Test that Access-Control-Allow-Origin header is set to *."""
    r = requests.get(f"{base_url}/status", timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.headers.get("Access-Control-Allow-Origin") == "*"

def test_cors_allow_methods_header(base_url):
    """Test that Access-Control-Allow-Methods includes GET and POST."""
    r = requests.get(f"{base_url}/status", timeout=TIMEOUT)
    allowed = r.headers.get("Access-Control-Allow-Methods", "")
    assert "GET" in allowed
    assert "POST" in allowed

def test_cors_allow_headers(base_url):
    """Test that Access-Control-Allow-Headers includes Authorization."""
    r = requests.get(f"{base_url}/status", timeout=TIMEOUT)
    allowed = r.headers.get("Access-Control-Allow-Headers", "")
    assert "Authorization" in allowed

def test_cors_headers_on_protected_endpoints(base_url):
    """Test that CORS headers are present even on 401 responses."""
    r = requests.get(f"{base_url}/usergroups", timeout=TIMEOUT)
    assert r.status_code == 401
    assert "Access-Control-Allow-Origin" in r.headers


# ---------------------------------------------------------------------------
# CORS preflight
# ---------------------------------------------------------------------------

def test_options_request_returns_204(base_url):
    """Test that OPTIONS requests return 204 No Content."""
    r = requests.options(f"{base_url}/status", timeout=TIMEOUT)
    assert r.status_code == 204

def test_options_includes_allow_methods(base_url):
    """Test that OPTIONS response includes allowed methods."""
    r = requests.options(f"{base_url}/status", timeout=TIMEOUT)
    assert r.status_code == 204
    assert "Access-Control-Allow-Methods" in r.headers

def test_options_includes_allow_headers(base_url):
    """Test that OPTIONS response includes allowed headers."""
    r = requests.options(f"{base_url}/status", timeout=TIMEOUT)
    assert "Access-Control-Allow-Headers" in r.headers

def test_options_includes_max_age(base_url):
    """Test that OPTIONS response includes max age of 86400."""
    r = requests.options(f"{base_url}/status", timeout=TIMEOUT)
    assert r.headers.get("Access-Control-Max-Age") == "86400"
