# Parent image
FROM nginx:1.17.2

LABEL version="0.1.0"

# Remove the default config file that
# /etc/nginx/nginx.conf includes
RUN rm /etc/nginx/conf.d/default.conf

COPY app.conf /etc/nginx/conf.d

COPY favicon.ico /usr/share/nginx/html

# Nginx will listen on port 80 inside the container
EXPOSE 80