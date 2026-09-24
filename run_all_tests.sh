#!/bin/bash
# Run all HuBMAP Gateway integration tests for a given environment.
# Each API must have its container running before executing this script.
#
# Usage:
#   ./run_all_tests.sh [ENV]
#
# ENV defaults to "localhost" if not specified.
#
# Examples:
#   ./run_all_tests.sh
#   ./run_all_tests.sh localhost
#   ./run_all_tests.sh dev
#
# To run a single API:
#   cd tests
#   TEST_ENV="localhost" TEST_API="entity-api" pytest integration/entity-api/ -m "not requires_auth" -v

set -e

ENV="${1:-localhost}"
TESTS_DIR="$(dirname "$0")/tests"

echo "Running integration tests for environment: ${ENV}"
echo

cd "$TESTS_DIR"

echo "=== entity-api ==="
TEST_ENV="${ENV}" TEST_API="entity-api" pytest integration/entity-api/ -m "not requires_auth"

echo "=== hs-ontology-api ==="
TEST_ENV="${ENV}" TEST_API="hs-ontology-api" pytest integration/hs-ontology-api/ -m "not requires_auth"

echo "=== search-api ==="
TEST_ENV="${ENV}" TEST_API="search-api" pytest integration/search-api/ -m "not requires_auth"

echo "=== uuid-api ==="
TEST_ENV="${ENV}" TEST_API="uuid-api" pytest integration/uuid-api/ -m "not requires_auth"
