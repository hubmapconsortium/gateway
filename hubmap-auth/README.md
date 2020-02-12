## HuBMAP Auth Container

This is the HuBMAP Auth service written in Python Flask served with uWSGI application server in conjunction with Nginx (as reverse proxy) in a docker container. All HuBMAP API services requests that require authentication and authorization will come to this gateway first.

### Flask config

The Flask application confiuration file `app.cfg` is located under `instance` folder. You can read more about [Flask Instance Folders](http://flask.pocoo.org/docs/1.0/config/#instance-folders). In this config file, you can specify the following items:

````
# File path of API endpoints json file, DO NOT MODIFY
API_ENDPOINTS_FILE = '/usr/src/app/api_endpoints.json'

# File path of the secured datasets
SECURED_DATASETS_FILE = '/usr/src/app/secured_datasets.json'

# Globus app client ID and secret
GLOBUS_APP_ID = ''
GLOBUS_APP_SECRET = ''

# The maximum integer number of entries in the cache queue
CACHE_MAXSIZE = 128
# Expire the cache after the time-to-live (seconds)
CACHE_TTL = 7200
````

### uWSGI config

In the `hubmap-auth/Dockerfile`, we installed uWSGI and the uWSGI Python plugin via yum. There's also a uWSGI configuration file `src/uwsgi.ini` and it tells uWSGI the details of running this Flask app. No need to modify.

### Nginx config

Nginx serves as the reverse proxy and passes the requests to the uWSGI server. The nginx configuration file for this service is located at `nginx/conf.d-dev/hubmap-auth.conf` or `nginx/conf.d-prod/hubmap-auth.conf` under the root project. This file defines how the `hubmap-auth` container handles the API requests via nginx using the `auth_request` module.


### API Endpoints Lookup and Caching

For API auth of the Web Gateway, we'll need a json file named `api_endpoints.json` defined in the `instance/app.cfg` that specifies all the details for matching endpoints. Public endpoints don't require any authentication. However, the private endpoints will require the globus token in the `Authorization` header or the custom `MAuthorization` HTTP header. Certain endpoints that require certain group access will also require the globus group access token. 

Note: this endpoints file will be mounted to the docker container when we spin up the service. The mount point is defined in the docker-compose ymal file based on your environment.

When the API client/consumer sends out the `Authorization` HTTP header, a valid token should be used:

````
Authorization: Bearer u8kr4P3XwePdWgoJ2N7Q9MDMNQK5MDgMNWYe2on5xQEVyQPlxpIqCOjYoX41qXyYEdQzVN9np2jQMniPpDJ74c7LXztq9mYc10GQU6d0x
````

Note this token needs to be a group access token (nexus token) if the requested endpoint requires group access, otherwise a regular auth token works.

And if the API client uses the custom `MAuthorization` header instead of `Authorization` header, follow the format:

````
MAuthorization: MBearer {"auth_token": "u8kr4P3XwePdWgoJ2N7Q9MDMNQK5MDgMNWYe2on5xQEVyQPlxpIqCOjYoX41qXyYEdQzVN9np2jQMniPpDJ74c7LXztq9mYc10GQU6d0x", "nexus_token": "dexYbd9jMOqkN9JGBYK49lPzgM5JQxxnm2YkXvd2Q8lYJgKDqas8CkrwXzBrMMoW9DowKzEYQeEgdmCqPv0NJKQwd8", "transfer_token": "AghvlgEPx7gDg9YKwnQBgYvBKoBXqjdYProGavWOK76Oj0p4E3cgCKNMV2adlxwBWw7150E3Bk594rTKDd4joUplYg"}
````

To make the lookup of a given endpoint more efficent, we enabled caching. The caching settings can be found in the `instance/app.cfg` file:

````
# The maximum integer number of entries in the cache queue
CACHE_MAXSIZE = 128
# Expire the cache after the time-to-live (seconds)
CACHE_TTL = 7200
````

When the data source of the `endpoints.json` gets updated, we'll need to clear the cache by calling this endpoint (in the case of local development mode):

````
GET http://localhost:8080/cache_clear
````