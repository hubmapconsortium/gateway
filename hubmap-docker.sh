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

function echo_help () {
    echo "Usage: $0 [-vhN] [localhost|dev|test|stage|prod] [build|start|stop|check|config]"
    echo "       -v verbose"
    echo "       -h help"
    echo "       -N use --no-cache for build"
}

# Command line parsing.  See for ex. https://sookocheff.com/post/bash/parsing-bash-script-arguments-with-shopts/
# and https://stackoverflow.com/questions/3466166/how-to-check-if-running-in-cygwin-mac-or-linux
unameOut="$(uname -s)"
case "${unameOut}" in
    Linux*)     machine=Linux;;
    Darwin*)    machine=Mac;;
    CYGWIN*)    machine=Cygwin;;
    MINGW*)     machine=MinGw;;
    *)          machine="UNKNOWN:${unameOut}"
esac
BUILD_OPTS=
VERBOSE=
if [ "$machine" = 'Mac' ] ; then
    options=$(getopt vhN "$@")
else
    options=$(getopt -o vhN -- "$@")
fi
[ $? -eq 0 ] || {
    echo "Incorrect option provided"
    echo_help
    exit 1
}
eval set -- "$options"
while true; do
    case "$1" in
        -N|--no-cache)
            BUILD_OPTS+="--no-cache"
            ;;
    -v)
        VERBOSE=1
        ;;
    -h)
        echo_help
        exit 0
        ;;
    --)
        shift
        break
        ;;
    esac
    shift
done
if [ -n "$VERBOSE" ] ; then
    echo 'BUILD_OPTS' $BUILD_OPTS
    echo '$1' $1
    echo '$2' $2
fi

if [[ "$1" != "localhost" && "$1" != "dev" && "$1" != "test" && "$1" != "stage" && "$1" != "prod" ]]; then
    echo "Unknown build environment '$1', specify one of the following: 'localhost', 'dev', 'test', 'stage', or 'prod'"
    exit 255
fi

if [[ "$2" != "build" && "$2" != "start" && "$2" != "stop" && "$2" != "check" && "$2" != "config" ]]; then
    echo "Unknown command '$2', specify 'build' or 'start' or 'stop' or 'check' or 'config' as the second argument"
    exit 255
fi

# set DIR to be the directory of the current script
get_dir_of_this_script
if [ -n "$VERBOSE" ] ; then
    echo 'DIR is ' $DIR
fi

# set some environment variables which may be used by the docker-compose scripts
if [ -e $DIR/../ingest-pipeline/build_number ] ; then
    export INGEST_PIPELINE_BUILD_NUM=`cat $DIR/../ingest-pipeline/build_number`
fi

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

if [ -n "$VERBOSE" ] ; then
    echo 'INGEST_PIPELINE_BUILD_NUM is ' $INGEST_PIPELINE_BUILD_NUM
    echo 'HOST_UID is ' $HOST_UID
    echo 'HOST_GID is ' $HOST_GID
fi

if [ "$2" = "build" ]; then
    # First create the shared docker network
    cd $DIR
    docker network create gateway_hubmap

    # Build images for gateway since this is the current dir
    ./docker-setup.sh
    docker-compose -f docker-compose.yml -f docker-compose.$1.yml build $BULD_OPTS

    cd $DIR/../uuid-api/docker
    ./docker-setup.sh
    docker-compose -f docker-compose.yml -f docker-compose.$1.yml build $BUILD_OPTS

    cd $DIR/../entity-api/docker
    ./docker-setup.sh
    docker-compose -f docker-compose.yml -f docker-compose.$1.yml build $BUILD_OPTS

    cd $DIR/../search-api/docker
    ./docker-setup.sh
    docker-compose -f docker-compose.yml -f docker-compose.$1.yml build $BUILD_OPTS

    # Only have ingest-api and ingest-ui on the same host machine for localhost environment
    # dev, test, or prod deployment has ingest-api on a separate machine
    cd $DIR/../ingest-ui/docker
    ./docker-setup-ingest-ui.sh
    docker-compose -f docker-compose-ingest-ui.$1.yml build $BULD_OPTS
    
    # Also build ingest-api and ingest-pipeline for localhost only
    if [ "$1" = "localhost" ]; then
        cd $DIR/../ingest-ui/docker
        ./docker-setup-ingest-api.$1.sh
        docker-compose -f docker-compose-ingest-api.$1.yml build  $BUILD_OPTS
    
        cd $DIR/../ingest-pipeline/docker
        ./docker-setup.$1.sh
        docker-compose -f docker-compose.yml -f docker-compose.$1.yml build $BUILD_OPTS
    fi

elif [ "$2" = "start" ]; then
    # Spin up the containers for each project
    cd $DIR/../uuid-api/docker
    docker-compose -p uuid-api -f docker-compose.yml -f docker-compose.$1.yml up -d

    cd $DIR/../entity-api/docker
    docker-compose -p entity-api -f docker-compose.yml -f docker-compose.$1.yml up -d

    cd $DIR/../search-api/docker
    docker-compose -p search-api -f docker-compose.yml -f docker-compose.$1.yml up -d
    
    # Only have ingest-api and ingest-ui on the same host machine for localhost environment
    # dev, test, or prod deployment has ingest-api on a separate machine

    cd $DIR/../ingest-ui/docker
    docker-compose -p ingest-ui -f docker-compose-ingest-ui.$1.yml up -d

    # Also start the ingest-api and ingest-pipeline for localhost only
    if [ "$1" = "localhost" ]; then
        cd $DIR/../ingest-ui/docker
        docker-compose -p ingest-api -f docker-compose-ingest-api.$1.yml up -d
    
        cd $DIR/../ingest-pipeline/docker
        ./docker-setup.$1.sh
        docker-compose -p ingest-pipeline -f docker-compose.yml -f docker-compose.$1.yml up -d
    fi

    # The last one is gateway since nginx conf files require 
    # entity-api, uuid-api, ingest-ui, ingest-api, and ingest-pipeline to be running
    # before starting the gateway service
    cd $DIR
    docker-compose -p gateway -f docker-compose.yml -f docker-compose.$1.yml up -d

elif [ "$2" = "stop" ]; then
    # Stop the gateway first
    cd $DIR
    docker-compose -p gateway -f docker-compose.yml -f docker-compose.$1.yml stop

    # Stop each service

    # Only have ingest-api and ingest-ui on the same host machine for localhost environment
    # dev, test, or prod deployment has ingest-api on a separate machine
    cd $DIR/../ingest-ui/docker
    docker-compose -p ingest-ui -f docker-compose-ingest-ui.$1.yml stop

    # Also stop the ingest-api and ingest-pipeline containers for localhost only
    if [ "$1" = "localhost" ]; then
        cd $DIR/../ingest-ui/docker
        docker-compose -p ingest-api -f docker-compose-ingest-api.$1.yml stop
    
        cd $DIR/../ingest-pipeline/docker
        docker-compose -p ingest-pipeline -f docker-compose.yml -f docker-compose.$1.yml stop
    fi

    cd $DIR/../uuid-api/docker
    docker-compose -p uuid-api -f docker-compose.yml -f docker-compose.$1.yml stop

    cd $DIR/../entity-api/docker
    docker-compose -p entity-api -f docker-compose.yml -f docker-compose.$1.yml stop

    cd $DIR/../search-api/docker
    docker-compose -p search-api -f docker-compose.yml -f docker-compose.$1.yml stop
elif [ "$2" = "config" ]; then
    # Export the VERSION as environment variable in each project
    cd $DIR
    export HUBMAP_AUTH_VERSION=`cat VERSION`
    echo "###### GATEWAY $HUBMAP_AUTH_VERSION ########"
    docker-compose -p gateway -f docker-compose.yml -f docker-compose.$1.yml config

    # Only have ingest-api and ingest-ui on the same host machine for localhost environment
    # dev, test, or prod deployment has ingest-api on a separate machine
    cd $DIR/../ingest-ui/docker
    export INGEST_UI_VERSION=`cat ../VERSION`
    echo "###### INGEST-UI $INGEST_UI_VERSION ########"
    docker-compose -p ingest-ui -f docker-compose-ingest-ui.$1.yml config

    # ingest-api and ingest-pipeline containers for localhost only
    if [ "$1" = "localhost" ]; then
        cd $DIR/../ingest-ui/docker
        export INGEST_API_VERSION=`cat ../VERSION`
        echo "###### INGEST-API $INGEST_API_VERSION ########"
        docker-compose -p ingest-api -f docker-compose-ingest-api.$1.yml config
        
        cd $DIR/../ingest-pipeline/docker
        echo "###### INGEST-PIPELINE ########"
        docker-compose -p ingest-pipeline -f docker-compose.yml -f docker-compose.$1.yml config
    fi

    cd $DIR/../uuid-api/docker
    export UUID_API_VERSION=`cat ../VERSION`
    echo "###### UUID-API $UUID_API_VERSION ########"
    docker-compose -p uuid-api -f docker-compose.yml -f docker-compose.$1.yml config

    cd $DIR/../entity-api/docker
    export ENTITY_API_VERSION=`cat ../VERSION`
    echo "###### ENTITY-API $ENTITY_API_VERSION ########"
    docker-compose -p entity-api -f docker-compose.yml -f docker-compose.$1.yml config

    cd $DIR/../search-api/docker
    export SEARCH_API_VERSION=`cat ../VERSION`
    echo "###### SEARCH-API $SEARCH_API_VERSION ########"
    docker-compose -p search-api -f docker-compose.yml -f docker-compose.$1.yml config
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

    echo 'Checks complete, all good :)'
fi
