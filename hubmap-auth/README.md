## HuBMAP Auth Container

This is the HuBMAP Auth service written in Python Flask served with uWSGI and Nginx in a docker container. All API access requests that require authentication and authorization will come to this gateway first.

### Nginx config

This `hubmap-auth.conf` needs to be placed in the `nginx/conf.d` folder under the root project. This file defines how the `hubmap-auth` container handles the API requests via nginx using the `auth_request` module.

````
server {
    # The hubmap-auth service listens port 80 on it's container
    # Will need to map to a port on the host at deployment
    # Currently we use 8080 from the host defined in the docker-compose.yml
    listen 80;
    
    server_name localhost;
    root /usr/share/nginx/html;

    # Logging to the mounted volume for outside container access
    access_log /usr/src/app/log/nginx_access_hubmap-auth.log;
    error_log /usr/src/app/log/nginx_error_hubmap-auth.log warn;
    
    location = /favicon.ico {
        alias /usr/share/nginx/html/favicon.ico;
    }
    
    # Let the flask application (listens port 5000 on the same container) to verify API requests
    location / { 
        include uwsgi_params;
        uwsgi_pass localhost:5000;
    }

}
````

### API Endpoints Lookup and Caching

For API auth of the Web Gateway, we'll need a json file named `endpoints.json` that specifies all the public and private endpoints. Public endpoints don't require any authentication. However, the private endpoints will require the globus `auth_token` in the custom `MAuthorization` HTTP header. Certain endpoints that require certain group access will also require the globus `nexus_token`. The Json file looks like below:

````json
{
  "public": [
    "GET http://localhost:8181/",
    "GET http://localhost:8181/status",
    "GET http://localhost:8181/favicon.ico"
  ],
  "private": [
    {
      "endpoint": "GET http://localhost:8181/invalid",
      "group": "fake-group-id"
    },
    {
      "endpoint": "GET http://localhost:8181/get",
      "group": "5777527e-ec11-11e8-ab41-0af86edb4424"
    },
    {
      "endpoint": "POST http://localhost:8181/post",
      "group": "5bd084c8-edc2-11e8-802f-0e368f3075e8"
    },
    {
      "endpoint": "PUT http://localhost:8181/put",
      "group": "5bd084c8-edc2-11e8-802f-0e368f3075e8"
    }
  ]
}
````

And the `MAuthorization` header from requests looks like this:

````
MAuthorization: MBearer {"name": "User Name", "email": "useremail@example.com", "globus_id": "d0f8907a-ec78-48a7-9c85-7da995b65406", "auth_token": "u8kr4P3XwePdWgoJ2N7Q9MDMNQK5MDgMNWYe2on5xQEVyQPlxpIqCOjYoX41qXyYEdQzVN9np2jQMniPpDJ74c7LXztq9mYc10GQU6d0x", "nexus_token": "dexYbd9jMOqkN9JGBYK49lPzgM5JQxxnm2YkXvd2Q8lYJgKDqas8CkrwXzBrMMoW9DowKzEYQeEgdmCqPv0NJKQwd8", "transfer_token": "AghvlgEPx7gDg9YKwnQBgYvBKoBXqjdYProGavWOK76Oj0p4E3cgCKNMV2adlxwBWw7150E3Bk594rTKDd4joUplYg"}
````

To make the lookup of a given endpoint more efficent, we enabled caching. The caching settings can be found in the `instance/app.cfg` file:

````
# The maximum integer number of entries in the cache queue
CACHE_MAXSIZE = 128
# Expire the cache after the time-to-live (seconds)
CACHE_TTL = 7200
````

When the data source of the `endpoints.json` gets updated, we'll need to clear the cache by calling this endpoint:

````
GET http://localhost:8080/cache_clear
````