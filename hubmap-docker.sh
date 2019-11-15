#!/bin/bash

function absent_or_newer () {
    if  [ \( -e $1 \) -a \( $2 -nt $1 \) ]; then
	echo "$1 is out of date" ;
	exit -1
	fi
    }

if [[ "$1" != "dev" && "$1" != "prod" ]]; then
	echo "Unknown build environment '$1', specify either 'dev' or 'prod'"
else
    if [[ "$2" != "build" && "$2" != "start" && "$2" != "stop" && "$2" != "check" ]]; then
	echo "Unknown command '$2', specify 'build' or 'start' or 'stop' or 'check' as the second argument"
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
	elif [ "$2" == "check" ]; then
	    for pth in '../ingest-ui/src/ingest-ui/.env' '../ingest-ui/src/ingest-api/instance/app.cfg' \
		       '../gateway/hubmap-auth/src/instance/app.cfg' ; do
		if [ ! -e $pth ]; then
		    echo "missing $pth" ; exit -1
		fi
	    done

	    absent_or_newer ../ingest-ui/docker/ingest-ui/src ../ingest-ui/src/ingest-ui
	    absent_or_newer ../ingest-ui/docker/ingest-api/src ../ingest-ui/src/ingest-api
	    absent_or_newer ../uuid-api/docker/uuid-api/src ../uuid-api/src/uuid-api
	    absent_or_newer ../entity-api/docker/entity-api/src ../entity-api/src/entity-api

	    echo 'checks complete'
	fi
    fi
fi

