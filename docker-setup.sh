#!/bin/bash

# Set the version environment variable for the docker build
# Version number is from the VERSION file
# Also remove newlines and leading/trailing slashes if present in that VERSION file
export HUBMAP_AUTH_VERSION=$(tr -d "\n\r" < VERSION | xargs)
echo "HUBMAP_AUTH_VERSION: $HUBMAP_AUTH_VERSION"

