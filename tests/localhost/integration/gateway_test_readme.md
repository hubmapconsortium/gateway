# HubMap-Auth Localhost Integration Tests

Integration tests for hubmap-auth localhost deployment. These tests verify that hubmap-auth runs correctly in a Docker container and provides authorization services to other APIs on the `gateway_hubmap` Docker network.

## Test Files

This directory contains tests organized by functionality:

- **test_endpoints_public.py** - Public endpoints (no auth required)
- **test_endpoints_protected.py** - Protected endpoints (auth required)
- **test_authorization.py** - Authorization logic (/api_auth behavior)
- **test_configuration.py** - Configuration file validation
- **test_cors.py** - CORS headers and preflight
- **test_cache.py** - Cache management endpoints

Files are named to group together alphabetically by purpose (all `test_endpoints_*` files group together, etc.).

## Prerequisites

### Running Containers
The tests require hubmap-auth to be running in Docker:

```bash
cd gateway
./docker-localhost.sh build
./docker-localhost.sh start

# Verify the container is healthy
docker ps | grep hubmap-auth
# STATUS should show "healthy"
```

### Python Environment
Tests are designed to run in a Python virtual environment:

```bash
# Create virtual environment (first time only)
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies (first time only)
pip install requests
```

## Running the Tests

### From gateway repository root

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all localhost integration tests
python -m unittest discover -s test/localhost/integration -p "test_*.py" -v
```

### Run specific test file

```bash
source .venv/bin/activate

# Run all public endpoint tests
python -m unittest tests.localhost.integration.test_endpoints_public -v

# Run all protected endpoint tests
python -m unittest tests.localhost.integration.test_endpoints_protected -v

# Run all authorization tests
python -m unittest tests.localhost.integration.test_authorization -v
```

### Run Specific Test Classes

```bash
source .venv/bin/activate

# Run just public GET endpoint tests
python -m unittest tests.localhost.integration.test_endpoints_public.EndpointsGETPublicTests -v

# Run just protected DELETE endpoint tests
python -m unittest tests.localhost.integration.test_endpoints_protected.EndpointsDELETEProtectedTests -v

# Run just authorization header validation tests
python -m unittest tests.localhost.integration.test_authorization.ApiAuthHeaderValidationTests -v
```

### Run Individual Tests

```bash
source .venv/bin/activate
python -m unittest tests.localhost.integration.test_endpoints_public.EndpointsGETPublicTests.test_status_json_responds -v
```

### Run with Verbose Output

Add `-v` flag for detailed output:

```bash
python -m unittest discover -s test -p "test_localhost_integration.py" -v
```

## Test Structure

### Test Classes

**HubMapAuthLocalhostTests**
- Core functionality tests for hubmap-auth
- Validates status endpoint responds correctly
- Tests `/api_auth` endpoint with various header combinations
- Validates performance requirements (< 1 second response)

**HubMapAuthEndpointCoverage**
- Tests authorization logic against `api_endpoints.localhost.json`
- Verifies public endpoints are accessible without authentication
- Verifies protected endpoints require authentication
- Uses parameterized subtests for comprehensive coverage

### Key Test Methods

- `test_status_endpoint_responds()` - Basic connectivity and response validation
- `test_api_auth_with_valid_headers_public_endpoint()` - Public endpoint authorization
- `test_api_auth_with_valid_headers_protected_endpoint_no_token()` - Protected endpoint blocking
- `test_api_endpoints_json_valid_format()` - Configuration file validation

## Best Practices Used

### Code Quality
- **Type hints** - All parameters and return types annotated for clarity
- **Docstrings** - Every test has descriptive documentation
- **Descriptive names** - Test names clearly describe what they verify
- **Proper assertions** - Meaningful assertion messages for failures

### Test Organization
- **Class-level constants** - `BASE_URL`, `TIMEOUT` defined once and reused
- **setUpClass** - Expensive setup (container checks) run once per class
- **subTest** - Parameterized tests provide clear failure reporting per endpoint
- **Focused tests** - Each test validates one specific behavior

### Robustness
- **Timeout handling** - All requests have explicit timeouts
- **Connection error handling** - Graceful failure with helpful messages
- **Conditional skipping** - Tests skip gracefully when Docker unavailable
- **Clear error messages** - Failures indicate exactly what went wrong and how to fix

### CI/CD Ready
- **No external dependencies** - Uses only standard library + requests
- **Subprocess isolation** - Docker commands use subprocess with timeout
- **Exit codes** - Proper test success/failure reporting
- **Environment agnostic** - Works in local development and CI pipelines

## Test Coverage

### What These Tests Verify

✅ hubmap-auth container starts and becomes healthy  
✅ Status endpoint responds with valid JSON  
✅ `/api_auth` endpoint validates required headers  
✅ Authorization logic checks `api_endpoints.localhost.json`  
✅ Public endpoints allow access without authentication  
✅ Protected endpoints block access without authentication  
✅ Unknown services are rejected  
✅ Missing headers are properly handled  
✅ Configuration file has valid JSON structure  

### What These Tests Don't Cover

❌ Token validation with real Globus tokens (requires valid credentials)  
❌ Group membership validation (requires test users in specific groups)  
❌ Load testing / performance under stress  
❌ Security penetration testing  
❌ Multi-container orchestration failures  

## Troubleshooting

### "Cannot connect to hubmap-auth"
**Cause:** Container not running or not accessible  
**Solution:**
```bash
cd gateway
./docker-localhost.sh start
docker ps | grep hubmap-auth
```

### "hubmap-auth not ready: status.json returned 500"
**Cause:** Container running but application not initialized  
**Solution:** Check container logs for errors
```bash
docker logs hubmap-auth
```

### "Docker not available - skipping test"
**Cause:** Docker commands failing or timing out  
**Solution:** Verify Docker is running
```bash
docker --version
docker ps
```

### Tests hang or timeout
**Cause:** Network connectivity issues between host and containers  
**Solution:** Verify port mappings and container networking
```bash
docker port hubmap-auth
curl http://localhost:7777/status.json
```

## Future Enhancements

### Pytest Migration (Optional)
While these tests use Python's built-in `unittest`, you can optionally migrate to pytest for additional features:

**Benefits of pytest:**
- More concise syntax with simple `assert` statements
- Better parameterized testing with `@pytest.mark.parametrize`
- Richer output formatting and failure reporting
- Extensive plugin ecosystem (coverage, parallel execution, etc.)
- Fixture system for complex setup/teardown

**Migration effort:** Low - pytest runs unittest tests without modification

**To use pytest (optional):**
```bash
pip install pytest
pytest test/test_localhost_integration.py -v
```

**Recommendation:** Stick with unittest for now unless you need pytest-specific features. Unittest is part of Python's standard library and sufficient for these integration tests.

## Contributing

When adding new tests:

1. **Follow existing patterns** - Use the same class structure and naming conventions
2. **Add docstrings** - Every test should explain what it validates
3. **Use subTest for parameters** - When testing multiple similar cases
4. **Handle failures gracefully** - Provide actionable error messages
5. **Keep tests independent** - Each test should work in isolation
6. **Update this README** - Document new test classes or significant changes

## CI/CD Integration

These tests are designed to run in GitHub Actions or similar CI/CD systems:

```yaml
# Example GitHub Actions workflow
- name: Start hubmap-auth
  run: |
    cd gateway
    ./docker-localhost.sh build
    ./docker-localhost.sh start
    
- name: Wait for healthy status
  run: |
    timeout 60 bash -c 'until docker ps | grep hubmap-auth | grep healthy; do sleep 2; done'
    
- name: Run integration tests
  run: |
    source .venv/bin/activate
    python -m unittest discover -s test -p "test_localhost_integration.py" -v
```

## Related Documentation

- [Docker Deployment Guide](../README.md) - How to deploy hubmap-auth locally
- [API Endpoints Configuration](../api_endpoints.localhost.json) - Authorization configuration
- [HubMap-Auth API Documentation](../hubmap-auth/README.md) - API reference
