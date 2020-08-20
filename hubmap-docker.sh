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

# The `absent_or_newer` checks if the copied src at docker/some-api/src directory exists 
# and if the source src directory is newer. 
# If both conditions are true `absent_or_newer` writes an error message 
# and causes hubmap-docker.sh to exit with an error code.
function absent_or_newer () {
    if  [ \( -e $1 \) -a \( $2 -nt $1 \) ]; then
        echo "$1 is out of date"
        exit -1
    fi
}

if [[ "$1" != "localhost" && "$1" != "dev" && "$1" != "test" && "$1" != "stage" && "$1" != "prod" ]]; then
    echo "Unknown build environment '$1', specify one of the following: localhost|dev|test|stage|prod"
    exit 255
fi

if [[ "$2" != "check" && "$2" != "config" && "$2" != "build" && "$2" != "start" && "$2" != "stop" ]]; then
    echo "Unknown command '$2', specify one of the following: check|config|build|start|stop"
    exit 255
fi

# set DIR to be the directory of the current script
get_dir_of_this_script
echo 'DIR is ' $DIR

# Use the current user UID and GID to run processes in containers
if [ "$1" = "localhost" ]; then
    if [ -z "$HOST_UID" ] ; then
        log_name=`logname`
        export HOST_UID=`id -u $log_name`
    fi
    if [ -z "$HOST_GID" ] ; then
        log_name=`logname`
        export HOST_GID=`id -g $log_name`
    fi
fi

echo 'HOST_UID is ' $HOST_UID
echo 'HOST_GID is ' $HOST_GID

if [ "$2" = "build" ]; then
    # First create the shared docker network
    docker network create gateway_hubmap

    # Build images for gateway since this is the current dir
    # Use the `source` command to execute ./docker-setup.sh in the current process 
    # since that script contains export environment variable
    cd $DIR
    ./hubmap-auth-docker.sh $1 build

    cd $DIR/../uuid-api/docker
    ./uuid-api-docker.sh $1 build

    cd $DIR/../entity-api/docker
    ./entity-api-docker.sh $1 build

    cd $DIR/../search-api/docker
    ./search-api-docker.sh $1 build

    # Only have ingest-api and ingest-ui on the same host machine for localhost environment
    # dev, test, or prod deployment has ingest-api on a separate machine
    cd $DIR/../ingest-ui/docker
    ./ingest-ui-docker.sh $1 build
    
    # Also build ingest-api and ingest-pipeline for localhost only
    if [ "$1" = "localhost" ]; then
        cd $DIR/../ingest-ui/docker
        ./ingest-api-docker.sh $1 build
    
        cd $DIR/../ingest-pipeline/docker
        source ./docker-setup.$1.sh
        ./ingest-pipeline-docker.sh $1 build
    fi

elif [ "$2" = "start" ]; then
    # Spin up the containers for each project
    cd $DIR/../uuid-api/docker
    ./uuid-api-docker.sh $1 start

    cd $DIR/../entity-api/docker
    ./entity-api-docker.sh $1 start

    cd $DIR/../search-api/docker
    ./search-api-docker.sh $1 start
    
    # Only have ingest-api and ingest-ui on the same host machine for localhost environment
    # dev, test, or prod deployment has ingest-api on a separate machine

    cd $DIR/../ingest-ui/docker
    ./ingest-ui-docker.sh $1 start

    # Also start the ingest-api and ingest-pipeline for localhost only
    if [ "$1" = "localhost" ]; then
        cd $DIR/../ingest-ui/docker
        ./ingest-api-docker.sh $1 start
    
        cd $DIR/../ingest-pipeline/docker
        ./docker-setup.$1.sh
        ./ingest-pipeline-docker.sh $1 start
    fi

    # The last one is gateway since nginx conf files require 
    # entity-api, uuid-api, ingest-ui, ingest-api, and ingest-pipeline to be running
    # before starting the gateway service
    cd $DIR
    ./hubmap-auth-docker.sh $1 start

elif [ "$2" = "stop" ]; then
    # Stop the gateway first
    cd $DIR
    ./hubmap-auth-docker.sh $1 stop

    # Stop each service

    # Only have ingest-api and ingest-ui on the same host machine for localhost environment
    # dev, test, or prod deployment has ingest-api on a separate machine
    cd $DIR/../ingest-ui/docker
    ./ingest-ui-docker.sh $1 stop

    # Also stop the ingest-api and ingest-pipeline containers for localhost only
    if [ "$1" = "localhost" ]; then
        cd $DIR/../ingest-ui/docker
        ./ingest-api-docker.sh $1 stop
    
        cd $DIR/../ingest-pipeline/docker
        ./ingest-pipeline-docker.sh $1 stop
    fi

    cd $DIR/../uuid-api/docker
    ./uuid-api-docker.sh $1 stop

    cd $DIR/../entity-api/docker
    ./entity-api-docker.sh $1 stop

    cd $DIR/../search-api/docker
    ./search-api-docker.sh $1 stop
elif [ "$2" = "config" ]; then
    # Export the VERSION as environment variable in each project
    cd $DIR
    echo "###### GATEWAY ########"
    ./hubmap-auth-docker.sh $1 config

    # Only have ingest-api and ingest-ui on the same host machine for localhost environment
    # dev, test, or prod deployment has ingest-api on a separate machine
    cd $DIR/../ingest-ui/docker
    echo "###### INGEST-UI ########"
    ./ingest-ui-docker.sh $1 config

    # ingest-api and ingest-pipeline containers for localhost only
    if [ "$1" = "localhost" ]; then
        cd $DIR/../ingest-ui/docker
        echo "###### INGEST-API ########"
        ./ingest-api-docker.sh $1 config
        
        cd $DIR/../ingest-pipeline/docker
        echo "###### INGEST-PIPELINE ########"
        ./ingest-pipeline-docker.sh $1 config
    fi

    cd $DIR/../uuid-api/docker
    echo "###### UUID-API ########"
    ./uuid-api-docker.sh $1 config

    cd $DIR/../entity-api/docker
    echo "###### ENTITY-API ########"
    ./entity-api-docker.sh $1 config

    cd $DIR/../search-api/docker
    echo "###### SEARCH-API ########"
    ./search-api-docker.sh $1 config
elif [ "$2" = "check" ]; then
    # Bash array
    config_paths=(
        '../gateway/hubmap-auth/src/instance/app.cfg'
        '../uuid-api/src/instance/app.cfg'
        '../entity-api/src/instance/app.cfg'
        '../search-api/src/instance/app.cfg'
        '../ingest-ui/src/ingest-ui/.env'
    )

    # Add ingest-api and ingest-pipeline configs to the array for localhost only
    if [ "$1" = "localhost" ]; then
        config_paths+=(
            '../ingest-ui/src/ingest-api/instance/app.cfg'
            '../ingest-pipeline/src/ingest-pipeline/instance/app.cfg'
        )
    fi

    cd $DIR
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

    # Good sign when you see it
    echo 'Checks complete, all good :)'
fi
