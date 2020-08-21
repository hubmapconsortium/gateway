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

if [[ "$2" != "check" && "$2" != "config" && "$2" != "build" && "$2" != "start" && "$2" != "stop" && "$2" != "down" ]]; then
    echo "Unknown command '$2', specify one of the following: check|config|build|start|stop|down"
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


# Direct the execution to individual script for each project
cd $DIR/../uuid-api/docker
./uuid-api-docker.sh $1 $2

cd $DIR/../entity-api/docker
./entity-api-docker.sh $1 $2

cd $DIR/../search-api/docker
./search-api-docker.sh $1 $2

# Only have ingest-api and ingest-ui on the same host machine for localhost environment
# dev/test/staage/prod deployment has ingest-api on a separate machine

cd $DIR/../ingest-ui/docker
./ingest-ui-docker.sh $1 $2

# Also start the ingest-api and ingest-pipeline for localhost only
if [ "$1" = "localhost" ]; then
    cd $DIR/../ingest-ui/docker
    ./ingest-api-docker.sh $1 $2

    cd $DIR/../ingest-pipeline/docker
    ./ingest-pipeline-docker.sh $1 $2
fi

# The last one is gateway since nginx conf files require all proxied services to be running prior to the nignx start
cd $DIR
./hubmap-auth-docker.sh $1 $2
