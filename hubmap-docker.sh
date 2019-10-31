#!/bin/bash

if [[ "$1" != "dev" && "$1" != "prod" ]]; then
	echo "Unknown build environment '$1', specify either 'dev' or 'prod'"
else
	if [[ "$2" != "build" && "$2" != "start" && "$2" != "stop" ]]; then
		echo "Unknown command '$2', specify 'build' or 'start' or 'stop' as the second argument"
	else
        if [ "$2" = "build" ]; then
	        # First create the shared docker network
		    docker network create gateway_hubmap

			# Build images for gateway since this is the current dir
			docker-compose -f docker-compose.yml -f docker-compose.$1.yml build

	        cd ..

			cd uuid-api/docker
			./docker-setup.sh
			docker-compose -f docker-compose.yml -f docker-compose.$1.yml build

			cd ../../

			cd entity-api/docker
			./docker-setup.sh
			docker-compose -f docker-compose.yml -f docker-compose.$1.yml build
	 
	        cd ../../

			cd ingest-ui/docker
			./docker-setup.sh
			docker-compose -f docker-compose.yml -f docker-compose.$1.yml build
	    elif [ "$2" = "start" ]; then
	    	# Back to parent directory
			cd ..

			# Spin up the containers for each project
			cd uuid-api/docker
			docker-compose -p uuid-api_and_mysql -f docker-compose.yml -f docker-compose.$1.yml up -d

			cd ../../

			cd entity-api/docker
			docker-compose -p entity-api_and_neo4j -f docker-compose.yml -f docker-compose.$1.yml up -d
	 
	        cd ../../

			cd ingest-ui/docker
			docker-compose -p ingest-api -f docker-compose.yml -f docker-compose.$1.yml up -d

	        cd ../../

	        # The last one is gateway since nginx conf files require entity-api, uuid-api, and ingest-api running
		    # before starting the gateway service
			cd gateway
			docker-compose -p gateway -f docker-compose.yml -f docker-compose.$1.yml up -d
		elif [ "$2" = "stop" ]; then
			# Stop the gateway first
			docker-compose -p gateway -f docker-compose.yml -f docker-compose.$1.yml stop
	   
			# Back to parent dir
	        cd ..

	        # Stop the ingest-api
			cd ingest-ui/docker
			docker-compose -p ingest-api -f docker-compose.yml -f docker-compose.$1.yml stop

	        cd ../../

			cd uuid-api/docker
			docker-compose -p uuid-api_and_mysql -f docker-compose.yml -f docker-compose.$1.yml stop

			cd ../../

			cd entity-api/docker
			docker-compose -p entity-api_and_neo4j -f docker-compose.yml -f docker-compose.$1.yml stop
	    fi
    fi
fi

