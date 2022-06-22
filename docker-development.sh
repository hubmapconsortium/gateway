#!/bin/bash

# Print a new line and the banner
echo
echo "==================== HUBMAP-AUTH ===================="

# Set the version environment variable for the docker build
# Version number is from the VERSION file
# Also remove newlines and leading/trailing slashes if present in that VERSION file
# Note: the BUILD and VERSION files are in the same dir as this script, this is different from other APIs
function export_version() {
    export HUBMAP_AUTH_VERSION=$(tr -d "\n\r" < VERSION | xargs)
    echo "HUBMAP_AUTH_VERSION: $HUBMAP_AUTH_VERSION"
}

# Generate the build version based on git branch name and short commit hash and write into BUILD file
# Note: the BUILD and VERSION files are in the same dir as this script, this is different from other APIs
function generate_build_version() {
    GIT_BRANCH_NAME=$(git branch | sed -n -e 's/^\* \(.*\)/\1/p')
    GIT_SHORT_COMMIT_HASH=$(git rev-parse --short HEAD)
    # Clear the old BUILD version and write the new one
    truncate -s 0 BUILD
    # Note: echo to file appends newline
    echo $GIT_BRANCH_NAME:$GIT_SHORT_COMMIT_HASH >> BUILD
    # Remmove the trailing newline character
    truncate -s -1 BUILD

    echo "BUILD(git branch name:short commit hash): $GIT_BRANCH_NAME:$GIT_SHORT_COMMIT_HASH"
}

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
    echo 'DIR of script:' $DIR
}


if [[ "$1" != "check" && "$1" != "config" && "$1" != "build" && "$1" != "start" && "$1" != "stop" && "$1" != "down" ]]; then
    echo "Unknown command '$1', specify one of the following: check|config|build|start|stop|down"
else
    # Always show the script dir
    get_dir_of_this_script

    # Always export and show the version
    export_version

    # Always show the build in case branch changed or new commits
    generate_build_version

    # Print empty line
    echo

    if [ "$1" = "check" ]; then
        # Bash array
        config_paths=(
            'hubmap-auth/src/instance/app.cfg'
        )

        for pth in "${config_paths[@]}"; do
            if [ ! -e $pth ]; then
                echo "Missing file (relative path to DIR of script) :$pth"
                exit -1
            fi
        done

        echo 'Checks complete, all good :)'
    elif [ "$1" = "config" ]; then
        docker-compose -f docker-compose.yml -f docker-compose.development.yml -p gateway config
    elif [ "$1" = "build" ]; then
        docker-compose -f docker-compose.yml -f docker-compose.development.yml -p gateway build
    elif [ "$1" = "start" ]; then
        docker-compose -f docker-compose.yml -f docker-compose.development.yml -p gateway up -d
    elif [ "$1" = "stop" ]; then
        docker-compose -f docker-compose.yml -f docker-compose.development.yml -p gateway stop
    elif [ "$1" = "down" ]; then
        docker-compose -f docker-compose.yml -f docker-compose.development.yml -p gateway down
    fi
fi

