# Nginx maintenance page for ingest-ui and portal-ui

This directory gets mounted to the `hubmap-auth` container's `/usr/share/nginx/html/`. The `/usr/share/nginx/html/ingest-ui` and `/usr/share/nginx/html/portal-ui` directories are being used as the document root to serve the maintenance page respectively.

To bring up the maintenance page for each UI website, simply create a file named `maintenance.on` under `/usr/share/nginx/html/ingest-ui` or `/usr/share/nginx/html/portal-ui`. Once the maintenance is completed, simply delete that file.
