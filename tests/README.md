# HubMap-Auth Test Suite

This directory contains all tests for the hubmap-auth service, organized by test type and deployment environment.

## Directory Structure

```
test/
├── README.md                    # This file - test suite overview
├── localhost/                   # Tests for localhost Docker deployment
│   ├── integration/            # Integration tests with other services
│   └── performance/            # Performance benchmarks (future)
└── [existing test files]       # Other test types
```

## Test Categories

### Localhost Tests (`localhost/`)

Tests for hubmap-auth running in Docker Desktop for local development and proof-of-concept deployments.

**When to run:** Before pushing changes that affect localhost deployment, Docker configuration, or authorization logic.

**See:** [localhost/README.md](localhost/README.md)

### Integration Tests (`localhost/integration/`)

End-to-end tests verifying hubmap-auth integrates correctly with other APIs (entity-api, ingest-api, etc.) over the `gateway_hubmap` Docker network.

**See:** [localhost/integration/README.md](localhost/integration/README.md)

### Performance Tests (`localhost/performance/`) - Future

Load testing and performance benchmarks for localhost deployment.

## Quick Start

### Run All Tests

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests
python -m unittest discover -s test -v
```

### Run Localhost Integration Tests Only

```bash
source .venv/bin/activate
python -m unittest discover -s test/localhost/integration -v
```

### Prerequisites

1. **Docker containers running:**
   ```bash
   cd gateway
   ./docker-localhost.sh start
   docker ps | grep hubmap-auth  # Should show "healthy"
   ```

2. **Python virtual environment:**<br>
Tests use the same dependencies as the main application:<br>
✅ Uses the exact same requests version as the application<br>
✅ No version conflicts or drift<br>
✅ Simpler - one source of truth for dependencies<br>
✅ Tests run with the same environment as the app<br>
```bash
# Create virtual environment (first time only)
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install application dependencies (includes requests)
pip install -r hubmap-auth/src/requirements.txt
```

## CI/CD Integration

These tests are designed to run in GitHub Actions or similar CI/CD systems. Example workflow:

```yaml
name: Localhost Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Create Docker network
        run: docker network create gateway_hubmap
      
      - name: Start hubmap-auth
        run: |
          cd gateway
          ./docker-localhost.sh build
          ./docker-localhost.sh start
      
      - name: Wait for healthy status
        run: timeout 60 bash -c 'until docker ps | grep hubmap-auth | grep healthy; do sleep 2; done'
      
      - name: Install test dependencies
        run: |
          python -m venv .venv
          source .venv/bin/activate
          pip install -r test/localhost/integration/requirements.txt
      
      - name: Run integration tests
        run: |
          source .venv/bin/activate
          python -m unittest discover -s test/localhost/integration -v
```

## Contributing

When adding new tests:

1. **Choose the right directory** - Place tests in the appropriate subdirectory based on type
2. **Follow existing patterns** - Match the style and structure of existing tests
3. **Add documentation** - Update relevant README files
4. **Keep tests independent** - Each test should run in isolation
5. **Use descriptive names** - Test names should clearly indicate what they verify
6. **Handle errors gracefully** - Provide actionable error messages

## Test Execution Order

Tests are discovered and run alphabetically by default. If execution order matters:

1. Use `setUpClass` and `tearDownClass` for class-level setup
2. Use `setUp` and `tearDown` for test-level setup
3. Name test files to control discovery order if needed

## Getting Help

- **Test failures:** Check container logs with `docker logs hubmap-auth`
- **Connection errors:** Verify containers are running with `docker ps`
- **Import errors:** Ensure virtual environment is activated
- **Docker issues:** Check Docker Desktop is running

## Related Documentation

- [HubMap-Auth Deployment Guide](../README.md)
- [API Endpoints Configuration](../api_endpoints.localhost.json)
- [Docker Compose Configuration](../docker-compose.localhost.yml)
