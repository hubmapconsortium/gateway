## HuBMAP Sample API Container

This is a sample API service written in Python Flask served with uWSGI in a docker container. All requests will be directed to the subrequest endpoint `/api_auth` which validates the authentication and authorizatiuon through the Web Gateway service on the `hubmap-auth` container.

### uWSGI config

Our sample API is written in Python Flask, in order to serve this app we'll need to use uWSGI server. In the `hubmap-auth/Dockerfile`, we installed uWSGI and the uWSGI Python plugin via yum. There's also a uWSGI configuration file `src/uwsgi.ini` and it tells uWSGI the details of running this Flask app.

### Nginx config

Nginx serves as the reverse proxy and passes the requests to the uWSGI server. The nginx configuration file for this service is located at `nginx/conf.d-dev/sample-api.conf` or `nginx/conf.d-prod/sample-api.conf` under the root project. This file defines how the subreqeusts get proxied to `hubmap-auth` container via nginx. 

### API Endpoints

The API endpoints are specified in a json file named `api_endpoints.json` in the root directory of this gateway project and it is mounted to the `hubmap-auth` container. Public endpoints don't require any authentication. However, the private endpoints will require the globus access token.

When accessing the private endpoints, the API client/consumer needs to send out the `Authorization` HTTP header with a valid globus token:

````
Authorization: Bearer u8kr4P3XwePdWgoJ2N7Q9MDMNQK5MDgMNWYe2on5xQEVyQPlxpIqCOjYoX41qXyYEdQzVN9np2jQMniPpDJ74c7LXztq9mYc10GQU6d0x
````

Note this token needs to be a group access token (nexus token) if the requested endpoint requires group access, otherwise a regular auth token works.

And if the API client uses the custom `MAuthorization` header instead of `Authorization` header, follow the format:

````
MAuthorization: MBearer {"auth_token": "u8kr4P3XwePdWgoJ2N7Q9MDMNQK5MDgMNWYe2on5xQEVyQPlxpIqCOjYoX41qXyYEdQzVN9np2jQMniPpDJ74c7LXztq9mYc10GQU6d0x", "nexus_token": "dexYbd9jMOqkN9JGBYK49lPzgM5JQxxnm2YkXvd2Q8lYJgKDqas8CkrwXzBrMMoW9DowKzEYQeEgdmCqPv0NJKQwd8", "transfer_token": "AghvlgEPx7gDg9YKwnQBgYvBKoBXqjdYProGavWOK76Oj0p4E3cgCKNMV2adlxwBWw7150E3Bk594rTKDd4joUplYg"}
````
