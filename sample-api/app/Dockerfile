# Parent image
FROM python:3

LABEL version="0.1.0"

# Create app directory
WORKDIR /usr/src/app

# Copy the source code from host to image
COPY . .

# Install app dependencies
RUN pip install -r requirements.txt

# Expose the port uWSGI will listen on
EXPOSE 5001

# Finally, we run uWSGI with the ini file
CMD [ "uwsgi", "--ini", "uwsgi.ini" ]