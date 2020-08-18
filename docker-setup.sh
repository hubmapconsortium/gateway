#!/bin/bash

# Set the version environment variable for the docker build
# Version number is from the VERSION file
export HUBMAP_AUTH_VERSION=`cat VERSION`

echo "HUBMAP_AUTH_VERSION: $HUBMAP_AUTH_VERSION"

