# HuBMAP Gateway With Multi-Container Stack

The HuBMAP Web Gateway serves as an authentication and authorization gateway for the HuBMAP API services. All API requests will be proxied to this gateway service for authentication and authorization against Globus Auth before reaching to the API endpoints. As a result of this design, the API services no longer need to handle the authentication and authorization.

## Project structure

````
gateway
├── api_endpoints.json
├── docker-compose.yml
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── hubmap-auth
│   ├── Dockerfile
│   ├── log
│   ├── src
│   └── start.sh
├── nginx
│   ├── conf.d-dev
│   ├── conf.d-prod
│   └── html
└── sample-api
    ├── Dockerfile
    ├── log
    └── src
````

* `api_endpoints.json` is a lookup file of all the API endpoints. Public endpoints don't need authentication, but private endpoints will require the globus `auth_token` in the custom `MAuthorization` HTTP header. 

* `docker-compose.yml` defines all the services and container details, as well as mounted volumes and ports mapping.

* `docker-compose.dev.yml` should be used for local development along with the base `docker-compose.yml`

* `docker-compose.prod.yml` should be used for production along with the base `docker-compose.yml`

* `hubmap-auth` is the actual HuBMAP Web Gateway authentication and authorization service that verifies all the API requests. It basically sets up the uWSGI application server to launch the Python Flask application and Nginx to act as a front end reverse proxy.

* `nginx` is the folder used for mounting individual API config file of each API service and some static content, like favicon.ico. This folder is mounted to the `hubmap-auth` container using volumes.

* `sample-api` is an example API service builds its own docker image and runs its own container. In this example, the API service is created with Pythong Flask and serviced by uWSGI. But this image doesn't contain Nginx server. We only use `sample-api.conf` and ask the Nginx from `hubmap-auth` to proxy the API requests. That's why we also put the configuration file in the `nginx/conf.d-dev` and `nginx/conf.d-prod` folder for development and production purposes and it will be mounted to the `hubmap-auth` container when it's spun up.

Each service has its own `Dockerfile`. We can either build the image separately or use docker compose to build all images as a stack.

The `log` under each project is another volume mount, this allows us to access the log files generated from the running contianers on the host for easy debugging and monitoring.

### How to add new API service to this stack

The `sample-api` service is running a flask app behind uWSGi for demonstration purpose. Your API service can be created with Django and running behind Apache HTTP or whatever stack as long as you specify the port that `hubmap-auth` nginx exposes for your service, and the port exposed on your container that nginx can hand over after authentication/authorization in `your-api.conf`. 

To add new API service to the stack, you'll just need to follow the `sample-api` example, and add a new `conf` file (put it into `nginx/conf.d-dev` or `nginx/conf.d-prod` according to your environments) to instruct Nginx to handle the proxy pass by directing all the API requests to the `hubmap-auth` for authentication and authorization. And this is achieved through Nginx's `auth_request` module. 

## Overview of tools

- [Docker v19.03.2](https://docs.docker.com/install/)
- [Docker Compose](https://docs.docker.com/compose/install/)

Note: Docker Compose requires Docker to be installed and running first.

## Workflow

We first use individual `Dockerfile` to define the image for each service componment. Then with Docker Compose, we define all the services and their relation to each other in the `docker-compose.yml` file. This allows us to spin this multi-container application stack up in a single command which does everything that needs to be done to get it running. 

Note: Don't confuse with the term of `service` and `container` when we talk about Docker Compose. A service only runs one image, but it codifies the way that image runs&mdash;what ports it should use, how many replicas of the container should run so the service has the capacity it needs, and so on. That's why in `docker-compose.yml` we see `services` defined.

In our `docker-compose.yml` configuration, you'll also see the `volumes` for each service. We use volumes to mount the app source code to the container when it's spun up and the log file generated on the containers are also made reachable by mounting to the host via volumes. 

### Build images

````
sudo docker-compose build
````

The command will go through all services in the `docker-compose.yml` file and build the ones that have a build section defined. Use `sudo docker-compose build --no-cache` to avoid the cached layers.


### Start up services

In our local development environment, we'll use the additional `docker-compose.dev.yml` file:

````
sudo docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
````

For production, we may want to start the containers in the background and leaves them running using the additional `docker-compose.prod.yml` file with the `-d` flag (detached mode):

````
sudo docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
````

The production changes include:

* Removing any volume bindings for application code, so that code stays inside the container and can’t be changed from outside
* Binding to different ports on the host
* Run an `init` inside each container that forwards signals and reaps processes.
* Specifying a restart policy like `restart: always` to avoid downtime

### Stop the running services

````
sudo docker-compose stop
````
The above command stops all the running containers without removing them. It preserves containers, volumes, and networks, along with every modification made to them. The stopped containers can be started again with `docker-compose start`. 

Instead of stopping all the containers, you can also specifically stop a particular service:

````
sudo docker-compose stop <service-name>
````

### Restart services

````
sudo docker-compose restart
````

This restarts all stopped and running services. If you make changes to your `docker-compose.yml` configuration or the individual `Dockerfile` these changes are not reflected after running this restart command. You'll need to rebuild all the images.

To just restart a particular service but not other services:

````
sudo docker-compose restart <service-name>
````

### Reset the status of our project

````
sudo docker-compose down
````

This command stops containers and removes containers, networks, volumes, and images created by `docker-compose up`.

You can take `down` 1 step further and add the `-v` flag to remove all volumes too. This is great for doing a full blown reset on your environment by running:

````
sudo docker-compose down -v
````

## Debugging

We can list all running containers:

````
sudo docker container ls
````

Then we can get into a container's shell by running:

````
sudo docker exec -it <mycontainer> bash
````

If you ever need to make Nginx configuration changes but don't want to stop the `hubmap-auth` container, you can shell into this container like above, and do the following:

````
nginx -s reload
````

If by any chance, you have to restart the Nginx but keep the container running:

````
nginx -s stop
````

Then 

````
nginx -g 'daemon off;' &
````

We can't use the systemd commands due to the base image Centos7 disabled systemd by default.

## Share containers across multiple docker compose projects

With a micro-services architecture design, we probably want to share a single database container across two or more applications, so that they can access the same data. Docker and Docker Compose make this possible through the use of Docker networks, allowing containers from different compose projects to be attached to the same network.

### Step 1: get the source code of each project

Currently, you can run `uuid-api` and `entity-api` with the `gateway`. Git clone the source code of each project and put them under the same parent directory.

### Step 2: add configuration files for each project

Note: MySQL is defiend in the `docker-compose.yml` of the `uuid-api` and Neo4j gets defined in the `entity-api` project.

### Step 3: build docker images

In the `gateway` project:

````
#sudo docker-compose -f docker-compose.yml -f docker-compose.dev.yml build
````

For `uuid-api` and `entity-api`, the project structure is very similar and you'll do:

````
cd docker
./docker-setup.sh
sudo docker-compose -f docker-compose.yml -f docker-compose.dev.yml build
````

### Step 4: spin up the containers in each project

We'll create the containers in `gateway` first since it creates the shared network `gateway_hubmap`.

````
sudo docker-compose -p gateway -f docker-compose.yml -f docker-compose.dev.yml up -d
````

Note: here we specify the docker compose project with the `-p` to avoid "WARNING: Found orphan containers ..." due to the fact that docker compose uses the directory name as the default project name.

Then do spin up the containers in `uuid-api` and `entity-api` likewise.

### Step 5: shell into the MySQL container to load the database table sql

````
sudo docker exec -it <mysql container ID> bash
````

Inside the MySQL container:

````
cd /usr/src/uuid-api/sql
````

Import the `hm_uuids` table into the database:

````
root@hubmap-mysql:/usr/src/uuid-api/sql# mysql -u root -p hm_uuid < uuids-dev.sql
````

Now we have all the running pieces. For production deployment, just use the `docker-compose.prod.yml` instead of `docker-compose.dev.yml`.
