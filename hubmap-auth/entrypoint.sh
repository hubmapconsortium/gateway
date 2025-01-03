#!/bin/bash

# Use the DEPLOY_MODE value as conditions
DEPLOY_MODE=${DEPLOY_MODE}

# Pass the HOST_UID and HOST_UID from environment variables specified in the child image docker-compose
HOST_GID=${HOST_GID}
HOST_UID=${HOST_UID}

echo "Starting hubmap-auth container with the same host user UID: $HOST_UID and GID: $HOST_GID"

# Create a new user with the same host UID to run processes on container
# The Filesystem doesn't really care what the user is called,
# it only cares about the UID attached to that user
# Check if user already exists and don't recreate across container restarts
getent passwd $HOST_UID > /dev/null 2&>1
# $? is a special variable that captures the exit status of last task
if [ $? -ne 0 ]; then
    groupadd -r -g $HOST_GID hive
    useradd -r -u $HOST_UID -g $HOST_GID -m hive
fi

# When running Nginx as a non-root user, we need to create the pid file
# and give read and write access to /var/run/nginx.pid, /var/cache/nginx, and /var/log/nginx
# In individual nginx *.conf, also don't listen on ports 80 or 443 because 
# only root processes can listen to ports below 1024
touch /var/run/nginx.pid
chown -R hive:hive /var/run/nginx.pid
chown -R hive:hive /var/cache/nginx
chown -R hive:hive /var/log/nginx

# No SSL in localhost mode
if [ $DEPLOY_MODE != "localhost"  ]; then
    chown -R hive:hive /etc/letsencrypt
fi

# Lastly we use su-exec to execute our process "$@" as that user
# Remember CMD from a Dockerfile of child image gets passed to the entrypoint.sh as command line arguments
# "$@" is a shell variable that means "all the arguments"
exec /usr/local/bin/su-exec hive "$@"
