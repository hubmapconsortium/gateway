# Nginx maintenance page for ingest-ui and portal-ui

This directory gets mounted to the `hubmap-auth` container's `/usr/share/nginx/html/`. The `/usr/share/nginx/html/ingest-ui/maintenance` and `/usr/share/nginx/html/portal-ui/maintenance` directories are being used as the document root to serve the maintenance page respectively.

To bring up the maintenance page for each UI website, simply create a file named `maintenance.on` under `/usr/share/nginx/html/ingest-ui/maintenance` or `/usr/share/nginx/html/portal-ui/maintenance`. Once the maintenance is completed, simply delete that file.
