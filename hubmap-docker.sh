#!/bin/bash

function get_dir_of_this_script () {
    # This function sets DIR to the directory in which this script itself is found.
    # Thank you https://stackoverflow.com/questions/59895/how-to-get-the-source-directory-of-a-bash-script-from-within-the-script-itself
    SCRIPT_SOURCE="${BASH_SOURCE[0]}"
    while [ -h "$SCRIPT_SOURCE" ]; do # resolve $SCRIPT_SOURCE until the file is no longer a symlink
	DIR="$( cd -P "$( dirname "$SCRIPT_SOURCE" )" >/dev/null 2>&1 && pwd )"
	SCRIPT_SOURCE="$(readlink "$SCRIPT_SOURCE")"
	[[ $SCRIPT_SOURCE != /* ]] && SCRIPT_SOURCE="$DIR/$SCRIPT_SOURCE" # if $SCRIPT_SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
    done
    DIR="$( cd -P "$( dirname "$SCRIPT_SOURCE" )" >/dev/null 2>&1 && pwd )"
    }

function absent_or_newer () {
    if  [ \( -e $1 \) -a \( $2 -nt $1 \) ]; then
        echo "$1 is out of date"
        exit -1
    fi
}

if [[ "$1" != "localhost" && "$1" != "dev" && "$1" != "test" && "$1" != "prod" ]]; then
    echo "Unknown build environment '$1', specify one of the following: 'localhost', 'dev', 'test', or 'prod'"
else
    if [[ "$2" != "build" && "$2" != "start" && "$2" != "stop" && "$2" != "check" ]]; then
        echo "Unknown command '$2', specify 'build' or 'start' or 'stop' or 'check' as the second argument"
    else
	# set DIR to be the directory of the current script
	get_dir_of_this_script
	echo 'DIR is ' $DIR

	if [ "$2" = "build" ]; then
            # First create the shared docker network
	    cd $DIR
            docker network create gateway_hubmap

            # Build images for gateway since this is the current dir
            docker-compose -f docker-compose.yml -f docker-compose.$1.yml build

            cd $DIR/../uuid-api/docker
            ./docker-setup.sh
            docker-compose -f docker-compose.yml -f docker-compose.$1.yml build

            cd $DIR/../entity-api/docker
            ./docker-setup.sh
            docker-compose -f docker-compose.yml -f docker-compose.$1.yml build

            cd ../../

            cd search-api/docker
            ./docker-setup.sh
            docker-compose -f docker-compose.yml -f docker-compose.$1.yml build

            # Only have ingest-api and ingest-ui on the same host machine for localhost environment
            # dev, test, or prod deployment has ingest-api on a separate machine
            cd $DIR/../ingest-ui/docker
            ./docker-setup-ingest-ui.sh
            docker-compose -f docker-compose-ingest-ui.$1.yml build
            
            # Also build ingest-api for localhost only
            if [ "$1" = "localhost" ]; then
		cd $DIR/../ingest-ui/docker
                ./docker-setup-ingest-api.$1.sh
                docker-compose -f docker-compose-ingest-api.$1.yml build
            fi

	    # Only have ingest-pipeline on this host for localhost environment
	    if [ "$1" = "localhost" ]; then
		cd $DIR/../ingest-pipeline/docker
		./docker-setup-ingest-pipeline.$1.sh
		docker-compose -f docker-compose-ingest-pipeline.$1.yml build
	    fi
        elif [ "$2" = "start" ]; then
            # Back to parent directory
            cd ..

            # Spin up the containers for each project
            cd uuid-api/docker
            docker-compose -p uuid-api -f docker-compose.yml -f docker-compose.$1.yml up -d

            cd ../../

            cd entity-api/docker
            docker-compose -p entity-api -f docker-compose.yml -f docker-compose.$1.yml up -d

            cd ../../

            cd search-api/docker
            docker-compose -p search-api -f docker-compose.yml -f docker-compose.$1.yml up -d
            
            # Only have ingest-api and ingest-ui on the same host machine for localhost environment
            # dev, test, or prod deployment has ingest-api on a separate machine
            cd ../../

            cd ingest-ui/docker
            docker-compose -p ingest-ui -f docker-compose-ingest-ui.$1.yml up -d

            # Also start the ingest-api for localhost only
            if [ "$1" = "localhost" ]; then
                docker-compose -p ingest-api -f docker-compose-ingest-api.$1.yml up -d
            fi

            cd ../../

            # The last one is gateway since nginx conf files require 
            # entity-api, uuid-api, ingest-ui, and ingest-api to be running
            # before starting the gateway service
            cd gateway
            docker-compose -p gateway -f docker-compose.yml -f docker-compose.$1.yml up -d
        elif [ "$2" = "stop" ]; then
            # Stop the gateway first
            docker-compose -p gateway -f docker-compose.yml -f docker-compose.$1.yml stop

            # Back to parent dir and stop each service
            cd ..

            # Only have ingest-api and ingest-ui on the same host machine for localhost environment
            # dev, test, or prod deployment has ingest-api on a separate machine
            cd ingest-ui/docker
            docker-compose -p ingest-ui -f docker-compose-ingest-ui.$1.yml stop

            # Also stop the ingest-api container for localhost only
            if [ "$1" = "localhost" ]; then
                docker-compose -p ingest-api -f docker-compose-ingest-api.$1.yml stop
            fi

            cd ../../

            cd uuid-api/docker
            docker-compose -p uuid-api -f docker-compose.yml -f docker-compose.$1.yml stop

            cd ../../

            cd entity-api/docker
            docker-compose -p entity-api -f docker-compose.yml -f docker-compose.$1.yml stop

            cd ../../

            cd search-api/docker
            docker-compose -p search-api -f docker-compose.yml -f docker-compose.$1.yml stop
        elif [ "$2" = "check" ]; then
            # Bash array
            config_paths=(
                '../gateway/hubmap-auth/src/instance/app.cfg'
                '../uuid-api/src/instance/app.cfg'
                '../entity-api/src/instance/app.cfg'
                '../search-api/src/instance/app.cfg'
                '../ingest-ui/src/ingest-ui/.env'
            )

            # Add ingest-api config to the array for localhost and dev only
            if [ "$1" = "localhost" ]; then
                config_paths+=(
                    '../ingest-ui/src/ingest-api/instance/app.cfg'
                )
            fi

            for pth in "${config_paths[@]}"; do
                if [ ! -e $pth ]; then
                    echo "Missing $pth"
                    exit -1
                fi
            done

            # The `absent_or_newer` checks if the copied src at docker/some-api/src directory exists 
            # and if the source src directory is newer. 
            # If both conditions are true `absent_or_newer` writes an error message 
            # and causes hubmap-docker.sh to exit with an error code.
            absent_or_newer ../uuid-api/docker/uuid-api/src ../uuid-api/src
            absent_or_newer ../entity-api/docker/entity-api/src ../entity-api/src
            absent_or_newer ../search-api/docker/search-api/src ../search-api/src
            absent_or_newer ../ingest-ui/docker/ingest-ui/src ../ingest-ui/src/ingest-ui

            # Also check the ingest-api for localhost and dev only
            if [ "$1" = "localhost" ]; then
                absent_or_newer ../ingest-ui/docker/ingest-api/src ../ingest-ui/src/ingest-api
            fi

            echo 'Checks complete, all good :)'
        fi
    fi
fi
