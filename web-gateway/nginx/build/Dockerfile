# Parent image
FROM nginx:1.17.2

LABEL version="0.1.0"

# Create build and log directory
RUN mkdir -p /usr/src/app/build
RUN mkdir -p /usr/src/app/log

# Change to directory that contains the Dockerfile
WORKDIR /usr/src/app/build

# Remove the default config file
RUN rm /etc/nginx/conf.d/default.conf

COPY app.conf /etc/nginx/conf.d

COPY favicon.ico /usr/share/nginx/html

# Nginx will listen on port 80 inside the container
EXPOSE 80