## HuBMAP Sample API Container

This is a sample API service written in Python Flask served with uWSGI in a docker container. All requests will be directed to the subrequest endpoint `/api_auth` which validates the authentication and authorizatiuon through the Web Gateway service on the `hubmap-auth` container.

The requests will need to have the custom `MAuthorization` header like below:

````
MAuthorization: MBearer {"name": "User Name", "email": "useremail@example.com", "globus_id": "d0f8907a-ec78-48a7-9c85-7da995b65406", "auth_token": "u8kr4P3XwePdWgoJ2N7Q9MDMNQK5MDgMNWYe2on5xQEVyQPlxpIqCOjYoX41qXyYEdQzVN9np2jQMniPpDJ74c7LXztq9mYc10GQU6d0x", "nexus_token": "dexYbd9jMOqkN9JGBYK49lPzgM5JQxxnm2YkXvd2Q8lYJgKDqas8CkrwXzBrMMoW9DowKzEYQeEgdmCqPv0NJKQwd8", "transfer_token": "AghvlgEPx7gDg9YKwnQBgYvBKoBXqjdYProGavWOK76Oj0p4E3cgCKNMV2adlxwBWw7150E3Bk594rTKDd4joUplYg"}
````

The Web Gateway will validate the `auth_token` and `nexus_token` before allowing access to the requested resource endpoint.

### Nginx config

This `sample-api.conf` needs to be placed in the `nginx/conf.d` folder under the root project. This file defines how the `hubmap-auth` container handles the API requests via nginx. 

````
# Define the upstream hubmap-auth server
# This sever will be accessed via http://
# So we use "localhost:80" because port 80 is exposed on `hubmap-auth` container for nginx
upstream hubmap-auth-server {
    # hubmap-auth:80/api_auth is invalid syntax
    server localhost:80;
}

server {
    # Each API has its dedicated port, we use 81 for the sample-api exposed 
    # on `hubmap-auth` container for nginx
    # Will need to map to a port on the host at deployment
    # Currently we use 8181 from the host defined in the docker-compose.yml
    listen 81;
    
    server_name localhost;
    root /usr/share/nginx/html;

    # Logging to the mounted volume for outside container access
    access_log /usr/src/app/log/nginx_access_sample-api.log;
    error_log /usr/src/app/log/nginx_error_sample-api.log warn;

    # No auth_request for favicon    
    location = /favicon.ico {
        alias /usr/share/nginx/html/favicon.ico;
    }
    
    # Send all requests to the '/api_auth' endpoint for authentication and authorization   
    auth_request /api_auth;
    # Optionally add 'status' as returned by upstream proxy along with the request
    # We'll be able to use this $auth_status variable later
    #auth_request_set $auth_status $upstream_status;

    # Exact request URI matching
    location = /api_auth {
        internal;
        # Upstream hubmap-auth server
        # We can specify the endpoint `api_auth` here but not in the upstream definition
        proxy_pass http://hubmap-auth-server/api_auth;
        # No need to send the POST body
        proxy_pass_request_body off;
        proxy_set_header Content-Length "";
        proxy_set_header X-Original-Request-Method $request_method;
        proxy_set_header X-Original-URI $request_uri;
        proxy_set_header Host $http_host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Once authenticated/authorized, pass all requests to the uwsgi server
    location / { 
        include uwsgi_params;
        # Pass reqeusts to the uwsgi server using the "uwsgi" protocol on port 5000
        # Here "sample-api" is the hostname defined in `docker-compose.yml`
        # We have to use this hostname because the sample API is running on a different container
        uwsgi_pass uwsgi://sample-api:5000;
    }

}
````

### API Endpoints

The API endpoints are specified in a json file named `api_endpoints.json` in the root directory of this project and it is mounted to the `hubmap-auth` container. Public endpoints don't require any authentication. However, the private endpoints will require the globus `auth_token` in the custom `MAuthorization` HTTP header. Certain endpoints that require certain group access will also require the globus `nexus_token`. The Json file looks like below for this sample API service:

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

For example, we issue a GET request to the base URI without `MAuthorization` header due to it's a public endpoint:

````
GET  HTTP/1.1
Host: localhost:8181
````

You'll see the response:

````
Hello! This is HuBMAP sample API service :)
````

But but if we issue another GET request without `MAuthorization` header to one of the provate endpoints:

````
GET /get HTTP/1.1
Host: localhost:8181
````

You'll see the "401 Authorization Required" response. And once we add the `MAuthorization` header:

````
GET /get HTTP/1.1
Host: localhost:8181
MAuthorization: MBearer {"name": "Zhou Yuan", "email": "ZHY19@pitt.edu", "globus_id": "c0f8907a-ec78-48a7-9c85-7da995b05446", "auth_token": "AgYK54jY6znYY8dYgwM2kddjX00Q2DE6an5ElgzpgwKD2NKeE2cWC2O13bjB51Dv44v2DjpyWMnozpFV7E9rVH1ldYs3E0lIjX9BTJ4jD", "nexus_token": "AgVJyD1349M1QQDz3b4k1kz4Nw39Vej6y47YqQWEozeEGjWd07UbCVyjpW0kYvXEVy5pxnye0BKqGqHlXo6klC6Gzk", "transfer_token": "AgX7B8bkYz35wXwQBnwXPjB397WxBVXwMVDVzwJYP4xxBBV53KCwCaa3EBm36Ey4d2WJnJOQ7E1PXbt4nWQm4H8046"}v
````

You should be able to see the user has been authenticated and the group access has been authorized as well. And the server responses back the JSON like this:

````json
{
    "auth_token": "AgYK54jY6znYY8dYgwM2kddjX00Q2DE6an5ElgzpgwKD2NKeE2cWC2O13bjB51Dv44v2DjpyWMnozpFV7E9rVH1ldYs3E0lIjX9BTJ4jD",
    "email": "ZHY19@pitt.edu",
    "globus_id": "c0f8907a-ec78-48a7-9c85-7da995b05446",
    "name": "Zhou Yuan",
    "nexus_token": "AgVJyD1349M1QQDz3b4k1kz4Nw39Vej6y47YqQWEozeEGjWd07UbCVyjpW0kYvXEVy5pxnye0BKqGqHlXo6klC6Gzk",
    "transfer_token": "AgX7B8bkYz35wXwQBnwXPjB397WxBVXwMVDVzwJYP4xxBBV53KCwCaa3EBm36Ey4d2WJnJOQ7E1PXbt4nWQm4H8046"
}
````