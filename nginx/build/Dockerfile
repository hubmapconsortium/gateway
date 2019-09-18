# Parent image
FROM nginx:1.17.3

LABEL version="0.1.0"

# Change to directory that contains the Dockerfile
WORKDIR /usr/src/app/build

# Remove the default config file
RUN rm /etc/nginx/conf.d/default.conf

# Each API service has its own nginx configuration file
COPY auth.conf /etc/nginx/conf.d
COPY sample-api.conf /etc/nginx/conf.d

# favicon.ico
COPY favicon.ico /usr/share/nginx/html

# Each API has its dedicated port and needs to be exposed here 
# and mapped in `docker-compose.yml` so it gets published on the host
EXPOSE 80 81

# No need to use CMD since the base image starts nginx automatically