## HuBMAP Sample API Behind Web Gateway

This is a sample API service written in Python Flask served with uwsgi with Nginx. All requests will be directed to the subrequest endpoint `/api_auth` which validates the authentication and authorizatiuon through the web gateway hosted on another server.

The requests will need to have the custom `MAuthorization` header like below:

````
MAuthorization: MBearer {"name": "User Name", "email": "useremail@example.com", "globus_id": "d0f8907a-ec78-48a7-9c85-7da995b65406", "auth_token": "u8kr4P3XwePdWgoJ2N7Q9MDMNQK5MDgMNWYe2on5xQEVyQPlxpIqCOjYoX41qXyYEdQzVN9np2jQMniPpDJ74c7LXztq9mYc10GQU6d0x", "nexus_token": "dexYbd9jMOqkN9JGBYK49lPzgM5JQxxnm2YkXvd2Q8lYJgKDqas8CkrwXzBrMMoW9DowKzEYQeEgdmCqPv0NJKQwd8", "transfer_token": "AghvlgEPx7gDg9YKwnQBgYvBKoBXqjdYProGavWOK76Oj0p4E3cgCKNMV2adlxwBWw7150E3Bk594rTKDd4joUplYg"}
````

The Web Gateway will validate the `auth_token` and `nexus_token` before allowing access to the requested resource endpoint.

### Nginx config

````
server {
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/cyberschmoo.com-0003/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/cyberschmoo.com-0003/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
     
    server_name api.cyberschmoo.com;
    root /usr/share/nginx/html/api.cyberschmoo.com;
    access_log /var/log/nginx/access_api.cyberschmoo.com.log;
    error_log /var/log/nginx/error_api.cyberschmoo.com.log warn;
    
    # No auth_request for favicon    
    location = /favicon.ico {
        alias /usr/share/nginx/html/favicon.ico;
    }
    
    # Send all requests to the '/api_auth' endpoint for authentication and authorization   
    location / {
        auth_request /api_auth;
        # Optionally add 'status' as returned by upstream proxy along with the request
        # We'll be able to use this $auth_status variable later
        #auth_request_set $auth_status $upstream_status;
    }

    # Exact request URI matching
    location = /api_auth {
        internal;
        # Auth server
        proxy_pass https://auth.cyberschmoo.com/api_auth;
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
        uwsgi_pass unix:/run/hubmap-sample-api.sock;
    }

}
````

Anytime you make a change to a configuration file, you should reload Nginx.

````
sudo systemctl reload nginx
````

- Reloading keeps the server running while re-reading any configuration file updates.
- Reloading is safer than restarting because if a syntax error is noticed in a config file, it will not proceed with the reload and your server remains running.
- If there is a syntax error in a config file and you restart, it's possible the server will not restart correctly.


## uWSGI and Flask App

First we need to install all the dependencies of our Flask app before runing with uwsgi.

````
cd sample-api
pipenv install
````

`pipenv` will create a virtualenv located at `/home/zhy19/.local/share/virtualenvs/sample-api-btZtasuS`. And we'll need to tell uwsgi this location later.

Once uwsgi is installed, run the following command to start the server to serve the Flask app:

````
$ sudo uwsgi -s /run/hubmap-sample-api.sock -w wsgi:application -H /home/zhy19/.local/share/virtualenvs/sample-api-btZtasuS --chmod-socket=666
````
Note: permission of the socket file has to be 666 (660 won't work). Must run wsgi with `sudo`

Alternatively, change the owner and group of the socket file to `nginx` also does the trick:

````
$ sudo uwsgi -s /run/hubmap-sample-api.sock -w wsgi:application -H /home/zhy19/.local/share/virtualenvs/sample-api-btZtasuS --chown-socket=nginx:nginx
````

Here, we create and use the `uwsgi.ini` file to make things easier:

````
sudo uwsgi --ini uwsgi.ini
````

And the `uwsgi.ini` looks like below:

````
[uwsgi]
chdir = /home/zhy19/sample-api
module = wsgi:application

#location of log file
logto = /var/log/uwsgi/hubmap-sample-api.log

virtualenv = /home/zhy19/.local/share/virtualenvs/sample-api-btZtasuS

# master with 2 worker process (based on CPU number)
master = true
processes = 2

# use unix socket for integration with nginx
socket = /run/hubmap-sample-api.sock
chmod-socket = 666
# enable socket cleanup when process stop
vacuum = true

# ensure compatibility with init system
die-on-term = true
````

Note: we'll need to create the directory of `/var/log/uwsgi/` for the logging.

## Trouble Shooting

If you are running CentOS 7, it's very possible that you'll get "13 Permission Denied" error with accessing the socket file. You'll want to disable SELinux:

```
sudo setenforce 0
````

However, this change will be valid for the current runtime session only. To permanently disable SELinux on your CentOS 7 system, open and edit `/etc/selinux/config` file and set the `SELINUX mod` to `disabled`.

## Systemd

We also want to make uwsgi always available. Create a systemd file at `/etc/systemd/system` called `hubmap-sample-api.uwsgi.service` with the following content:

````
[Unit]
Description=uWSGI serivice for HuBAMP Sample API
After=syslog.target

[Service]
ExecStart=/bin/uwsgi --ini /home/zhy19/sample-api/uwsgi.ini
Restart=always
KillSignal=SIGQUIT
Type=notify
NotifyAccess=all

[Install]
WantedBy=multi-user.target
````

Then we'll be able to start the `hubmap-sample-api` uwsgi service with the command:

````
sudo systemctl start hubmap-sample-api.uwsgi
````

Check that it started without issues by typing:

````
sudo systemctl status hubmap-sample-api.uwsgi
````

If there were no errors, enable the service so that it starts at boot by typing:

````
sudo systemctl enable hubmap-sample-api.uwsgi
````

You can stop the service at any time by typing:

````
sudo systemctl stop hubmap-sample-api.uwsgi
````

