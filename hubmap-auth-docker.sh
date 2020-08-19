#!/bin/bash

if [[ "$1" != "localhost" && "$1" != "dev" && "$1" != "test" && "$1" != "stage" && "$1" != "prod" ]]; then
    echo "Unknown build environment '$1', specify one of the following: 'localhost', 'dev', 'test', 'stage', or 'prod'"
else
    if [[ "$2" != "build" && "$2" != "start" && "$2" != "stop" && "$2" != "check" && "$2" != "config" ]]; then
        echo "Unknown command '$2', specify 'build' or 'start' or 'stop' or 'check' or 'config' as the second argument"
    else
        if [ "$2" = "build" ]; then
            # Use the `source` command to execute ./docker-setup.sh in the current process 
            # since that script contains export environment variable
            source ./docker-setup.sh
            docker-compose -f docker-compose.yml -f docker-compose.$1.yml build
        elif [ "$2" = "start" ]; then
            docker-compose -p gateway -f docker-compose.yml -f docker-compose.$1.yml up -d
        elif [ "$2" = "stop" ]; then
            docker-compose -p gateway -f docker-compose.yml -f docker-compose.$1.yml stop
        elif [ "$2" = "check" ]; then
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
            export HUBMAP_AUTH_VERSION=$(tr -d "\n\r" < VERSION | xargs)
            echo "###### GATEWAY $HUBMAP_AUTH_VERSION ########"
            docker-compose -p gateway -f docker-compose.yml -f docker-compose.$1.yml config
        fi
    fi
fi
