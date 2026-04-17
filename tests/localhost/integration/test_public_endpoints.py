"""
Tests for public hubmap-auth endpoints accessible without authentication.

Public endpoints should be accessible to anyone without requiring a token.
These include status checks, informational endpoints, and read-only data.

Run all public endpoint tests:
    python -m unittest tests.localhost.integration.test_endpoints_public -v

Run just GET tests:
    python -m unittest tests.localhost.integration.test_endpoints_public.EndpointsGETPublicTests -v

Run just POST tests:
    python -m unittest tests.localhost.integration.test_endpoints_public.EndpointsPOSTPublicTests -v
"""

import unittest
import requests
from requests.exceptions import ConnectionError


class EndpointsGETPublicTests(unittest.TestCase):
    """Test public GET endpoints that don't require authentication."""

    BASE_URL = "http://localhost:7777"
    TIMEOUT = 10

    @classmethod
    def setUpClass(cls):
        """Verify hubmap-auth is accessible before running tests."""
        try:
            response = requests.get(f"{cls.BASE_URL}/status.json", timeout=cls.TIMEOUT)
            if response.status_code != 200:
                raise RuntimeError(
                    f"hubmap-auth not ready: status.json returned {response.status_code}"
                )
        except ConnectionError as e:
            raise RuntimeError(
                f"Cannot connect to hubmap-auth at {cls.BASE_URL}. "
                "Ensure container is running: cd gateway && ./docker-localhost.sh start"
            ) from e

    def test_status_json_responds(self):
        """Test that /status.json endpoint returns valid status."""
        response = requests.get(f"{self.BASE_URL}/status.json", timeout=self.TIMEOUT)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        
        data = response.json()
        self.assertIsInstance(data, dict)
        # Verify gateway section exists with version info
        self.assertIn("gateway", data)
        self.assertIn("version", data["gateway"])

    def test_status_json_performance(self):
        """Test that status endpoint responds within reasonable time."""
        response = requests.get(f"{self.BASE_URL}/status.json", timeout=self.TIMEOUT)
        
        # Multi-service status check may take longer than simple endpoints
        # Allow up to 3 seconds for comprehensive health check
        self.assertLess(response.elapsed.total_seconds(), 3.0)

    def test_status_json_includes_service_status(self):
        """Test that status includes information about dependent services."""
        response = requests.get(f"{self.BASE_URL}/status.json", timeout=self.TIMEOUT)
        
        data = response.json()
        # Should include status for various services
        self.assertIsInstance(data, dict)
        # At minimum should have gateway info
        self.assertGreater(len(data), 0)

    def test_status_json_valid_content_type(self):
        """Test that status endpoint returns proper JSON content type."""
        response = requests.get(f"{self.BASE_URL}/status.json", timeout=self.TIMEOUT)
        
        self.assertIn("application/json", response.headers.get("Content-Type", ""))

    def test_status_json_handles_errors_gracefully(self):
        """Test that status endpoint handles malformed requests gracefully."""
        # Request with invalid query parameters
        response = requests.get(
            f"{self.BASE_URL}/status.json",
            params={"invalid": "param"},
            timeout=self.TIMEOUT
        )
        
        # Should still return 200 (ignore unknown params) or proper error code
        self.assertIn(response.status_code, [200, 400])


class EndpointsPOSTPublicTests(unittest.TestCase):
    """Test public POST endpoints that don't require authentication."""

    BASE_URL = "http://localhost:7777"
    TIMEOUT = 10

    # Placeholder for future public POST endpoints
    # Currently hubmap-auth has no public POST endpoints
    pass


if __name__ == "__main__":
    unittest.main()
