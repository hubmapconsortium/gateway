#!/bin/bash

# First create the shared docker network
docker network create gateway_hubmap

# Build images for each project
cd ..

cd uuid-api/docker
./docker-setup.sh
docker-compose -f docker-compose.yml -f docker-compose.$1.yml build
docker-compose -p uuid-api_and_mysql -f docker-compose.yml -f docker-compose.$1.yml up -d

cd ../../

cd entity-api/docker
./docker-setup.sh
docker-compose -f docker-compose.yml -f docker-compose.$1.yml build
docker-compose -p entity-api_and_neo4j -f docker-compose.yml -f docker-compose.$1.yml up -d

cd ../../

cd ingest-api/docker
./docker-setup.sh
docker-compose -f docker-compose.yml -f docker-compose.$1.yml build
docker-compose -p ingest-api -f docker-compose.yml -f docker-compose.$1.yml up -d

cd ../../

# The last one is gateway
cd gateway
docker-compose -f docker-compose.yml -f docker-compose.$1.yml build
docker-compose -p gateway -f docker-compose.yml -f docker-compose.$1.yml up -d


