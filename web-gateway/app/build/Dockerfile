# Parent image
FROM python:3

LABEL version="0.1.0"

# Change to directory that contains the Dockerfile
WORKDIR /usr/src/app/build

# Copy the Dockerfile and requirements.txt from host to image
COPY . .

# Install app dependencies
RUN pip install -r requirements.txt

# The EXPOSE instruction informs Docker that the container listens on the specified network ports at runtime. 
# EXPOSE does not make the ports of the container accessible to the host.
EXPOSE 5000

# Finally, we run uWSGI with the ini file
WORKDIR /usr/src/app/src
CMD [ "uwsgi", "--ini", "uwsgi.ini" ]