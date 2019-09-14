## HuBMAP Sample API Service

This is a sample API service written in Python Flask served through the `sample-api-app` container and `sample-api-nginx` container with uwsgi with Nginx. All requests will be directed to the subrequest endpoint `/api_auth` which validates the authentication and authorizatiuon through the web gateway served by `web-gateway-app` contaienr and `web-gateway-nginx` container.

The requests will need to have the custom `MAuthorization` header like below:

````
MAuthorization: MBearer {"name": "User Name", "email": "useremail@example.com", "globus_id": "d0f8907a-ec78-48a7-9c85-7da995b65406", "auth_token": "u8kr4P3XwePdWgoJ2N7Q9MDMNQK5MDgMNWYe2on5xQEVyQPlxpIqCOjYoX41qXyYEdQzVN9np2jQMniPpDJ74c7LXztq9mYc10GQU6d0x", "nexus_token": "dexYbd9jMOqkN9JGBYK49lPzgM5JQxxnm2YkXvd2Q8lYJgKDqas8CkrwXzBrMMoW9DowKzEYQeEgdmCqPv0NJKQwd8", "transfer_token": "AghvlgEPx7gDg9YKwnQBgYvBKoBXqjdYProGavWOK76Oj0p4E3cgCKNMV2adlxwBWw7150E3Bk594rTKDd4joUplYg"}
````

The Web Gateway will validate the `auth_token` and `nexus_token` before allowing access to the requested resource endpoint.

### Nginx config

````
upstream gateway {
    # Port 80 is exposed on host `web-gateway-nginx`
    # web-gateway-nginx:80/api_auth is invalid
    server web-gateway-nginx:80;
}

server {
    listen 80;
    
    server_name localhost;
    root /usr/share/nginx/html;

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
        # Upstream auth server
        # We can specify the endpoint `api_auth` here but not in the upstream definition
        proxy_pass http://gateway/api_auth;
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

    # Once authenticated, handle all requests with the python code via uwsgi
    location / { 
        include uwsgi_params;
        # Here use the `sample-api-app` hostname defiened in `docker-compose.yml`
        uwsgi_pass sample-api-app:5000;
    }

}
````
