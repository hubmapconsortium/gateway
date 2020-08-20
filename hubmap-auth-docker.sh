#!/bin/bash

# Set the version environment variable for the docker build
# Version number is from the VERSION file
# Also remove newlines and leading/trailing slashes if present in that VERSION file
function export_version() {
    export HUBMAP_AUTH_VERSION=$(tr -d "\n\r" < VERSION | xargs)
    echo "HUBMAP_AUTH_VERSION: $HUBMAP_AUTH_VERSION"
}

if [[ "$1" != "localhost" && "$1" != "dev" && "$1" != "test" && "$1" != "stage" && "$1" != "prod" ]]; then
    echo "Unknown build environment '$1', specify one of the following: localhost|dev|test|stage|prod"
else
    if [[ "$2" != "check" && "$2" != "config" && "$2" != "build" && "$2" != "start" && "$2" != "stop" && "$2" != "down" ]]; then
        echo "Unknown command '$2', specify one of the following: check|config|build|start|stop|down"
    else
        if [ "$2" = "check" ]; then
            # Bash array
            config_paths=(
                '../hubmap-auth/src/instance/app.cfg'
            )

            for pth in "${config_paths[@]}"; do
                if [ ! -e $pth ]; then
                    echo "Missing $pth"
                    exit -1
                fi
            done

            echo 'Checks complete, all good :)'
        elif [ "$2" = "config" ]; then
            export_version
            docker-compose -p gateway -f docker-compose.yml -f docker-compose.$1.yml config
        elif [ "$2" = "build" ]; then
            export_version
            docker-compose -f docker-compose.yml -f docker-compose.$1.yml build
        elif [ "$2" = "start" ]; then
            export_version
            docker-compose -p gateway -f docker-compose.yml -f docker-compose.$1.yml up -d
        elif [ "$2" = "stop" ]; then
            export_version
            docker-compose -p gateway -f docker-compose.yml -f docker-compose.$1.yml stop
        elif [ "$2" = "down" ]; then
            export_version
            docker-compose -p gateway -f docker-compose.yml -f docker-compose.$1.yml down
        fi
    fi
fi
