# Localhost Testing for HubMap-Auth

This directory contains tests for hubmap-auth running in Docker Desktop on localhost. These tests verify the service works correctly in a local development/proof-of-concept environment before deployment to higher tiers (DEV, TEST, PROD).

## Purpose

Localhost tests serve multiple purposes:

1. **Pre-deployment verification** - Validate configuration changes before pushing to DEV
2. **Local development** - Quick feedback during feature development
3. **Proof-of-concept** - Demonstrate hubmap-auth integration with new APIs
4. **Regression testing** - Ensure changes don't break existing functionality

## Test Types

### Integration Tests (`integration/`)

End-to-end tests that verify hubmap-auth integrates correctly with other services over Docker networking.

**What they test:**
- Container startup and health
- Authorization logic with `api_endpoints.localhost.json`
- Communication with other APIs (entity-api, etc.)
- nginx auth_request flow
- Docker network connectivity

**See:** [integration/README.md](integration/README.md)

### Performance Tests (`performance/`) - Future

Benchmarks and load tests for localhost deployment.

**What they will test:**
- Response time under load
- Concurrent request handling
- Memory usage patterns
- Container resource limits

## Prerequisites

### 1. Docker Setup

Create the shared Docker network (one-time setup):
```bash
docker network create gateway_hubmap
```

### 2. Build and Start Containers

```bash
cd gateway
./docker-localhost.sh build
./docker-localhost.sh start

# Verify containers are healthy
docker ps
# hubmap-auth STATUS should show "healthy"
```

### 3. Python Environment
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

# HTTP client library for API testing
```
## Running Tests

### All Localhost Tests

```bash
source .venv/bin/activate
python -m unittest discover -s test/localhost -v
```

### Integration Tests Only

```bash
source .venv/bin/activate
python -m unittest discover -s test/localhost/integration -v
```

### Specific Test File

```bash
source .venv/bin/activate
python -m unittest test.localhost.integration.test_localhost_integration -v
```

## Environment Differences

Localhost deployment differs from higher tiers in several ways:

| Aspect | Localhost | DEV/TEST/PROD |
|--------|-----------|---------------|
| SSL/TLS | Disabled | Let's Encrypt certificates |
| Ports | 7777 (custom) | 80, 443 (standard) |
| Logging | Local files + Docker logs | CloudWatch Logs |
| Auth endpoints | `api_endpoints.localhost.json` | `api_endpoints.{dev\|test\|prod}.json` |
| Network | `gateway_hubmap` (Docker) | AWS VPC |
| Service discovery | Docker DNS | AWS Route53/ELB |

Tests in this directory account for these differences.

## Debugging Failed Tests

### Container Not Running

```bash
# Check container status
docker ps -a | grep hubmap-auth

# Check logs
docker logs hubmap-auth

# Restart if needed
cd gateway
./docker-localhost.sh down
./docker-localhost.sh start
```

### Container Not Healthy

```bash
# Check health status
docker inspect hubmap-auth | grep -A 10 Health

# Common causes:
# - Port 7777 already in use
# - nginx configuration error
# - Missing api_endpoints.localhost.json
```

### Connection Refused

```bash
# Verify port mapping
docker port hubmap-auth

# Test from host
curl http://localhost:7777/status.json

# Test from inside container
docker exec hubmap-auth curl http://localhost:7777/status.json
```

### Docker Network Issues

```bash
# Inspect network
docker network inspect gateway_hubmap

# Verify containers are on the network
docker network inspect gateway_hubmap | grep Name
```

## Adding New Test Types

When adding new test categories:

1. **Create subdirectory** under `test/localhost/`
2. **Add README.md** explaining the test type and how to run
3. **Add requirements.txt** if new dependencies needed
4. **Update this README** to document the new test type
5. **Follow best practices** from existing integration tests

## Related Documentation

- [Parent Test Suite Overview](../README.md)
- [Docker Localhost Deployment](../../README.md)
- [API Endpoints Configuration](../../api_endpoints.localhost.json)
