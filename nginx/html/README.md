# Nginx maintenance page

This directory gets mounted to the `hubmap-auth` container's `/usr/share/nginx/html/` to serve the needed static files especially for service maintenance.

To bring up the maintenance page for each UI website, simply create a file named `maintenance.on` under each service's document root directory described below. Once the maintenance is completed, simply delete that file.

## ingest-ui maintenance

The ingest-ui maintenace page runs on the same `hubmap-auth` container's port 5555. The document root directory is `/usr/share/nginx/html/ingest-ui-maintenance`.

## portal-ui maintenance

The portal-ui maintenace page runs on the same `hubmap-auth` container's port 8888. The document root directory is `/usr/share/nginx/html/portal-ui-maintenance`.


