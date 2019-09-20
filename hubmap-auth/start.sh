#!/bin/bash

# Start nginx in background
# 'daemon off;' is nginx configuration directive
nginx -g 'daemon off;' &

# Start uwsgi
uwsgi --ini /usr/src/app/src/uwsgi.ini