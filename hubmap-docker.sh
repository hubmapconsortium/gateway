#!/bin/bash

if [[ "$1" != "dev" && "$1" != "prod" ]]; then
	echo "Unknown build environment '$1', specify either 'dev' or 'prod'"
else
	# First create the shared docker network
	docker network create gateway_hubmap

	# Back to parent directory
	cd ..

	# Build images and spin up the containers for each project
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

	cd ingest-ui/docker
	./docker-setup.sh
	docker-compose -f docker-compose.yml -f docker-compose.$1.yml build
	docker-compose -p ingest-api -f docker-compose.yml -f docker-compose.$1.yml up -d

	cd ../../

	# The last one is gateway since nginx conf files require entity-api, uuid-api, and ingest-api running
	# before starting the gateway service
	cd gateway
	docker-compose -f docker-compose.yml -f docker-compose.$1.yml build
	docker-compose -p gateway -f docker-compose.yml -f docker-compose.$1.yml up -d

fi

