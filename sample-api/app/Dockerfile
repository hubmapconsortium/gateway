# Parent image
FROM python:3

LABEL version="0.1.0"

# Create app directory
WORKDIR /usr/src/app

# Copy the source code from host to image
COPY . .

# Install app dependencies
RUN pip install -r requirements.txt

# The EXPOSE instruction informs Docker that the container listens on the specified network ports at runtime. 
# EXPOSE does not make the ports of the container accessible to the host.
EXPOSE 5000

# Finally, we run uWSGI with the ini file
CMD [ "uwsgi", "--ini", "uwsgi.ini" ]