#!/bin/bash

# Print the banner
echo
echo '#     #        ######  #     #    #    ######     ######'                                     
echo '#     # #    # #     # ##   ##   # #   #     #    #     #  ####   ####  #    # ###### #####'
echo '#     # #    # #     # # # # #  #   #  #     #    #     # #    # #    # #   #  #      #    #'
echo '####### #    # ######  #  #  # #     # ######     #     # #    # #      ####   #####  #    #'
echo '#     # #    # #     # #     # ####### #          #     # #    # #      #  #   #      #####'
echo '#     # #    # #     # #     # #     # #          #     # #    # #    # #   #  #      #   #'
echo '#     #  ####  ######  #     # #     # #          ######   ####   ####  #    # ###### #    #'
echo

# This function sets DIR to the directory in which this script itself is found.
# Thank you https://stackoverflow.com/questions/59895/how-to-get-the-source-directory-of-a-bash-script-from-within-the-script-itself                                                                      
function get_dir_of_this_script () {
    SCRIPT_SOURCE="${BASH_SOURCE[0]}"
    while [ -h "$SCRIPT_SOURCE" ]; do # resolve $SCRIPT_SOURCE until the file is no longer a symlink
        DIR="$( cd -P "$( dirname "$SCRIPT_SOURCE" )" >/dev/null 2>&1 && pwd )"
        SCRIPT_SOURCE="$(readlink "$SCRIPT_SOURCE")"
        [[ $SCRIPT_SOURCE != /* ]] && SCRIPT_SOURCE="$DIR/$SCRIPT_SOURCE" # if $SCRIPT_SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
    done
    DIR="$( cd -P "$( dirname "$SCRIPT_SOURCE" )" >/dev/null 2>&1 && pwd )"
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
echo 'DIR of script:' $DIR

# Use the current user UID and GID to run processes in containers for localhost build
if [ "$1" = "localhost" ]; then
    if [ -z "$HOST_UID" ] ; then
        log_name=`logname`
        export HOST_UID=`id -u $log_name`
    fi
    if [ -z "$HOST_GID" ] ; then
        log_name=`logname`
        export HOST_GID=`id -g $log_name`
    fi

    echo 'HOST_UID:' $HOST_UID
    echo 'HOST_GID:' $HOST_GID
fi

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
    cd $DIR
    ./hubmap-auth-docker.sh $1 config

    # Only have ingest-api and ingest-ui on the same host machine for localhost environment
    # dev, test, or prod deployment has ingest-api on a separate machine
    cd $DIR/../ingest-ui/docker
    ./ingest-ui-docker.sh $1 config

    # ingest-api and ingest-pipeline containers for localhost only
    if [ "$1" = "localhost" ]; then
        cd $DIR/../ingest-ui/docker
        ./ingest-api-docker.sh $1 config
        
        cd $DIR/../ingest-pipeline/docker
        ./ingest-pipeline-docker.sh $1 config
    fi

    cd $DIR/../uuid-api/docker
    ./uuid-api-docker.sh $1 config

    cd $DIR/../entity-api/docker
    ./entity-api-docker.sh $1 config

    cd $DIR/../search-api/docker
    ./search-api-docker.sh $1 config
elif [ "$2" = "check" ]; then
    cd $DIR
    ./hubmap-auth-docker.sh $1 check

    # Only have ingest-api and ingest-ui on the same host machine for localhost environment
    # dev, test, or prod deployment has ingest-api on a separate machine
    cd $DIR/../ingest-ui/docker
    ./ingest-ui-docker.sh $1 check

    # ingest-api and ingest-pipeline containers for localhost only
    if [ "$1" = "localhost" ]; then
        cd $DIR/../ingest-ui/docker
        ./ingest-api-docker.sh $1 check
        
        cd $DIR/../ingest-pipeline/docker
        ./ingest-pipeline-docker.sh $1 check
    fi

    cd $DIR/../uuid-api/docker
    ./uuid-api-docker.sh $1 check

    cd $DIR/../entity-api/docker
    ./entity-api-docker.sh $1 check

    cd $DIR/../search-api/docker
    ./search-api-docker.sh $1 check
fi
