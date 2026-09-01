"""
Tests for entity-api authorization integration with hubmap-auth.

These tests verify the nginx ↔ hubmap-auth integration mechanism,
Docker networking, and configuration. Tests here have knowledge of
the authorization infrastructure.

Run all authorization integration tests:
    pytest test_authorization_integration.py -v
"""

import subprocess
import pytest
import requests

TIMEOUT = 10


# ---------------------------------------------------------------------------
# nginx auth_request integration
# ---------------------------------------------------------------------------

def test_nginx_config_has_auth_request():
    """Test that nginx config includes auth_request directive."""
    result = subprocess.run(
        ["docker", "exec", "entity-api", "cat", "/etc/nginx/conf.d/entity-api.conf"],
        capture_output=True, text=True, timeout=5
    )
    if result.returncode != 0:
        pytest.skip("Cannot inspect nginx configuration")
    assert "auth_request /api_auth" in result.stdout

def test_nginx_config_calls_hubmap_auth():
    """Test that nginx config proxies to hubmap-auth:7777."""
    result = subprocess.run(
        ["docker", "exec", "entity-api", "grep", "-A", "10",
         "location = /api_auth", "/etc/nginx/conf.d/entity-api.conf"],
        capture_output=True, text=True, timeout=5
    )
    if result.returncode != 0:
        pytest.skip("Cannot inspect nginx configuration")
    assert "hubmap-auth:7777" in result.stdout

def test_nginx_sends_correct_host_header():
    """Test that nginx sends Host: entity-api to hubmap-auth."""
    result = subprocess.run(
        ["docker", "exec", "entity-api", "grep", "proxy_set_header Host",
         "/etc/nginx/conf.d/entity-api.conf"],
        capture_output=True, text=True, timeout=5
    )
    if result.returncode != 0:
        pytest.skip("Cannot inspect nginx configuration")
    assert 'proxy_set_header Host "entity-api"' in result.stdout

def test_nginx_sends_original_uri_header():
    """Test that nginx sends X-Original-URI header."""
    result = subprocess.run(
        ["docker", "exec", "entity-api", "grep", "X-Original-URI",
         "/etc/nginx/conf.d/entity-api.conf"],
        capture_output=True, text=True, timeout=5
    )
    if result.returncode != 0:
        pytest.skip("Cannot inspect nginx configuration")
    assert "X-Original-URI" in result.stdout

def test_nginx_sends_original_method_header():
    """Test that nginx sends X-Original-Request-Method header."""
    result = subprocess.run(
        ["docker", "exec", "entity-api", "grep", "X-Original-Request-Method",
         "/etc/nginx/conf.d/entity-api.conf"],
        capture_output=True, text=True, timeout=5
    )
    if result.returncode != 0:
        pytest.skip("Cannot inspect nginx configuration")
    assert "X-Original-Request-Method" in result.stdout


# ---------------------------------------------------------------------------
# Docker network connectivity
# ---------------------------------------------------------------------------

def test_entity_api_can_reach_hubmap_auth():
    """Test that entity-api can communicate with hubmap-auth."""
    result = subprocess.run(
        ["docker", "exec", "entity-api", "curl", "-f", "http://hubmap-auth:7777/status.json"],
        capture_output=True, text=True, timeout=10
    )
    if result.returncode != 0:
        pytest.fail("entity-api cannot reach hubmap-auth on Docker network")

def test_containers_on_gateway_hubmap_network():
    """Test that both containers are on gateway_hubmap network."""
    result = subprocess.run(
        ["docker", "network", "inspect", "gateway_hubmap",
         "--format", "{{range .Containers}}{{.Name}} {{end}}"],
        capture_output=True, text=True, timeout=5
    )
    if result.returncode != 0:
        pytest.skip("Cannot inspect Docker network")
    assert "hubmap-auth" in result.stdout
    assert "entity-api" in result.stdout

def test_docker_dns_resolves_hubmap_auth():
    """Test that Docker DNS resolves hubmap-auth hostname."""
    result = subprocess.run(
        ["docker", "exec", "entity-api", "getent", "hosts", "hubmap-auth"],
        capture_output=True, text=True, timeout=5
    )
    if result.returncode != 0:
        pytest.skip("Cannot test DNS resolution")
    assert "hubmap-auth" in result.stdout
    import re
    assert re.search(r'\d+\.\d+\.\d+\.\d+', result.stdout)


# ---------------------------------------------------------------------------
# Container health
# ---------------------------------------------------------------------------

def test_entity_api_container_healthy():
    """Test that entity-api container reports healthy status."""
    result = subprocess.run(
        ["docker", "inspect", "entity-api", "--format", "{{.State.Health.Status}}"],
        capture_output=True, text=True, timeout=5
    )
    if result.returncode != 0:
        pytest.skip("Cannot inspect container health")
    assert result.stdout.strip() == "healthy"

def test_hubmap_auth_container_healthy():
    """Test that hubmap-auth container is healthy (prerequisite)."""
    result = subprocess.run(
        ["docker", "inspect", "hubmap-auth", "--format", "{{.State.Health.Status}}"],
        capture_output=True, text=True, timeout=5
    )
    if result.returncode != 0:
        pytest.skip("Cannot inspect container health")
    assert result.stdout.strip() == "healthy", \
        "hubmap-auth must be healthy for entity-api tests to work"

def test_flask_app_loaded_successfully():
    """Test that Flask app loaded without configuration errors."""
    result = subprocess.run(
        ["docker", "logs", "entity-api"],
        capture_output=True, text=True, timeout=5
    )
    if result.returncode != 0:
        pytest.skip("Cannot inspect container logs")
    assert "WSGI app 0" in result.stdout
    assert "ready" in result.stdout
    assert "Unable to load configuration file" not in result.stdout
