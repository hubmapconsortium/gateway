# Parent image
FROM nginx:1.17.2

LABEL version="0.1.0"

# Remove the default config file that
# /etc/nginx/nginx.conf includes
RUN rm /etc/nginx/conf.d/default.conf

# We copy the requirements file in order to install
# Python dependencies
COPY app.conf /etc/nginx/conf.d

# Nginx will listen on this port
EXPOSE 80