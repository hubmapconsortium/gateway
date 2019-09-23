# Parent image
FROM python:3

LABEL version="0.1.0"

# Change to directory that contains the Dockerfile
WORKDIR /usr/src/app

# Copy from host to image
COPY . .

# Install app dependencies
# In this example, we install uwsgi as one of the app dependencies via pip
RUN pip install -r src/requirements.txt

# The EXPOSE instruction informs Docker that the container listens on the specified network ports at runtime. 
# EXPOSE does not make the ports of the container accessible to the host.
EXPOSE 5000

# Finally, we run uWSGI with the ini file
CMD [ "uwsgi", "--ini", "/usr/src/app/src/uwsgi.ini" ]