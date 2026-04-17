"""
Tests for protected hubmap-auth endpoints requiring authentication.

Protected endpoints should block access without valid tokens and proper
group membership. These tests verify authorization enforcement.

Run all protected endpoint tests:
    python -m unittest tests.localhost.integration.test_endpoints_protected -v

Run specific HTTP method tests:
    python -m unittest tests.localhost.integration.test_endpoints_protected.EndpointsGETProtectedTests -v
    python -m unittest tests.localhost.integration.test_endpoints_protected.EndpointsPOSTProtectedTests -v
"""

import unittest
import requests


class EndpointsGETProtectedTests(unittest.TestCase):
    """Test protected GET endpoints that require authentication."""

    BASE_URL = "http://localhost:7777"
    TIMEOUT = 10

    def test_usergroups_blocks_without_token(self):
        """Test that GET /usergroups requires authentication via entity-api."""
        headers = {
            "Host": "entity-api",
            "X-Original-URI": "/usergroups",
            "X-Original-Request-Method": "GET"
        }
        
        response = requests.get(
            f"{self.BASE_URL}/api_auth",
            headers=headers,
            timeout=self.TIMEOUT
        )
        
        self.assertEqual(response.status_code, 401)

    def test_datasets_unpublished_blocks_without_token(self):
        """Test that GET /datasets/unpublished requires authentication."""
        headers = {
            "Host": "entity-api",
            "X-Original-URI": "/datasets/unpublished",
            "X-Original-Request-Method": "GET"
        }
        
        response = requests.get(
            f"{self.BASE_URL}/api_auth",
            headers=headers,
            timeout=self.TIMEOUT
        )
        
        self.assertEqual(response.status_code, 401)

    def test_descendants_blocks_without_token(self):
        """Test that GET /descendants/<id> requires authentication."""
        headers = {
            "Host": "entity-api",
            "X-Original-URI": "/descendants/test-id",
            "X-Original-Request-Method": "GET"
        }
        
        response = requests.get(
            f"{self.BASE_URL}/api_auth",
            headers=headers,
            timeout=self.TIMEOUT
        )
        
        self.assertEqual(response.status_code, 401)

    def test_children_blocks_without_token(self):
        """Test that GET /children/<id> requires authentication."""
        headers = {
            "Host": "entity-api",
            "X-Original-URI": "/children/test-id",
            "X-Original-Request-Method": "GET"
        }
        
        response = requests.get(
            f"{self.BASE_URL}/api_auth",
            headers=headers,
            timeout=self.TIMEOUT
        )
        
        self.assertEqual(response.status_code, 401)

    def test_previous_revisions_blocks_without_token(self):
        """Test that GET /previous_revisions/<id> requires authentication."""
        headers = {
            "Host": "entity-api",
            "X-Original-URI": "/previous_revisions/test-id",
            "X-Original-Request-Method": "GET"
        }
        
        response = requests.get(
            f"{self.BASE_URL}/api_auth",
            headers=headers,
            timeout=self.TIMEOUT
        )
        
        self.assertEqual(response.status_code, 401)

    def test_next_revisions_blocks_without_token(self):
        """Test that GET /next_revisions/<id> requires authentication."""
        headers = {
            "Host": "entity-api",
            "X-Original-URI": "/next_revisions/test-id",
            "X-Original-Request-Method": "GET"
        }
        
        response = requests.get(
            f"{self.BASE_URL}/api_auth",
            headers=headers,
            timeout=self.TIMEOUT
        )
        
        self.assertEqual(response.status_code, 401)


class EndpointsPOSTProtectedTests(unittest.TestCase):
    """Test protected POST endpoints that require authentication."""

    BASE_URL = "http://localhost:7777"
    TIMEOUT = 10

    def test_datasets_components_blocks_without_token(self):
        """Test that POST /datasets/components requires authentication."""
        headers = {
            "Host": "entity-api",
            "X-Original-URI": "/datasets/components",
            "X-Original-Request-Method": "POST"
        }
        
        response = requests.get(
            f"{self.BASE_URL}/api_auth",
            headers=headers,
            timeout=self.TIMEOUT
        )
        
        self.assertEqual(response.status_code, 401)

    def test_entities_multiple_samples_blocks_without_token(self):
        """Test that POST /entities/multiple-samples/<count> requires authentication."""
        headers = {
            "Host": "entity-api",
            "X-Original-URI": "/entities/multiple-samples/5",
            "X-Original-Request-Method": "POST"
        }
        
        response = requests.get(
            f"{self.BASE_URL}/api_auth",
            headers=headers,
            timeout=self.TIMEOUT
        )
        
        self.assertEqual(response.status_code, 401)

    def test_entities_create_blocks_without_token(self):
        """Test that POST /entities/<type> requires authentication."""
        headers = {
            "Host": "entity-api",
            "X-Original-URI": "/entities/sample",
            "X-Original-Request-Method": "POST"
        }
        
        response = requests.get(
            f"{self.BASE_URL}/api_auth",
            headers=headers,
            timeout=self.TIMEOUT
        )
        
        self.assertEqual(response.status_code, 401)


class EndpointsPUTProtectedTests(unittest.TestCase):
    """Test protected PUT endpoints that require authentication."""

    BASE_URL = "http://localhost:7777"
    TIMEOUT = 10

    def test_entities_update_blocks_without_token(self):
        """Test that PUT /entities/<id> requires authentication."""
        headers = {
            "Host": "entity-api",
            "X-Original-URI": "/entities/test-uuid",
            "X-Original-Request-Method": "PUT"
        }
        
        response = requests.get(
            f"{self.BASE_URL}/api_auth",
            headers=headers,
            timeout=self.TIMEOUT
        )
        
        self.assertEqual(response.status_code, 401)

    def test_datasets_retract_blocks_without_token(self):
        """Test that PUT /datasets/<id>/retract requires admin authentication."""
        headers = {
            "Host": "entity-api",
            "X-Original-URI": "/datasets/test-id/retract",
            "X-Original-Request-Method": "PUT"
        }
        
        response = requests.get(
            f"{self.BASE_URL}/api_auth",
            headers=headers,
            timeout=self.TIMEOUT
        )
        
        # Requires Data Admin group
        self.assertEqual(response.status_code, 401)


class EndpointsDELETEProtectedTests(unittest.TestCase):
    """Test protected DELETE endpoints that require authentication."""

    BASE_URL = "http://localhost:7777"
    TIMEOUT = 10

    def test_flush_cache_blocks_without_token(self):
        """Test that DELETE /flush-cache/<id> requires authentication."""
        headers = {
            "Host": "entity-api",
            "X-Original-URI": "/flush-cache/test-id",
            "X-Original-Request-Method": "DELETE"
        }
        
        response = requests.get(
            f"{self.BASE_URL}/api_auth",
            headers=headers,
            timeout=self.TIMEOUT
        )
        
        self.assertEqual(response.status_code, 401)

    def test_flush_all_cache_blocks_without_token(self):
        """Test that DELETE /flush-all-cache requires admin authentication."""
        headers = {
            "Host": "entity-api",
            "X-Original-URI": "/flush-all-cache",
            "X-Original-Request-Method": "DELETE"
        }
        
        response = requests.get(
            f"{self.BASE_URL}/api_auth",
            headers=headers,
            timeout=self.TIMEOUT
        )
        
        # Requires Data Admin group
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
