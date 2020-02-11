#!/bin/bash

# Start nginx in background
# 'daemon off;' is nginx configuration directive
sudo nginx -g 'daemon off;' &

# Start uwsgi and keep it running in foreground
sudo uwsgi --ini /home/hubmap/src/uwsgi.ini