## HuBMAP Web Gateway Service

This is HuBMAP Web Gateway service written in Python Flask served through the `web-gateway-app` contaienr and `web-gateway-nginx` container. It requires the API requests to have the custom `MAuthorization` header like below:

````
MAuthorization: MBearer {"name": "User Name", "email": "useremail@example.com", "globus_id": "d0f8907a-ec78-48a7-9c85-7da995b65406", "auth_token": "u8kr4P3XwePdWgoJ2N7Q9MDMNQK5MDgMNWYe2on5xQEVyQPlxpIqCOjYoX41qXyYEdQzVN9np2jQMniPpDJ74c7LXztq9mYc10GQU6d0x", "nexus_token": "dexYbd9jMOqkN9JGBYK49lPzgM5JQxxnm2YkXvd2Q8lYJgKDqas8CkrwXzBrMMoW9DowKzEYQeEgdmCqPv0NJKQwd8", "transfer_token": "AghvlgEPx7gDg9YKwnQBgYvBKoBXqjdYProGavWOK76Oj0p4E3cgCKNMV2adlxwBWw7150E3Bk594rTKDd4joUplYg"}
````

The Web Gateway will validate the `auth_token` and `nexus_token` before allowing access to the requested resource endpoint.

### Nginx config

````
server {
    listen 80;
    
    server_name localhost;
    root /usr/share/nginx/html;
    
    location = /favicon.ico {
        alias /usr/share/nginx/html/favicon.ico;
    }
    
    location / { 
        include uwsgi_params;
        # Here use the `web-gateway-app` hostname defiened in `docker-compose.yml`
        uwsgi_pass web-gateway-app:5000;
    }

}
````
