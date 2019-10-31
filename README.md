# HuBMAP Gateway With Multi-Container Stack

The HuBMAP Web Gateway serves as an authentication and authorization gateway for the HuBMAP API services. All API requests will be proxied to this gateway service for authentication and authorization against Globus Auth before reaching to the API endpoints. As a result of this design, the API services no longer need to handle the authentication and authorization.

## Project structure

````
gateway
├── api_endpoints.dev.json
├── api_endpoints.prod.json
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

* `api_endpoints.dev.json` and `api_endpoints.dev.json` are lookup files of all the API endpoints for dev and prod environments. Public endpoints don't need authentication, but private endpoints will require the globus `auth_token` in the custom `MAuthorization` HTTP header. 

* `docker-compose.yml` defines all the services and container details, as well as mounted volumes and ports mapping. `docker-compose.dev.yml` should be used for local development along with the base `docker-compose.yml`. And `docker-compose.prod.yml` should be used for production along with the base `docker-compose.yml`

* `hubmap-auth` is the actual HuBMAP Web Gateway authentication and authorization service that verifies all the API requests. It basically sets up the uWSGI application server to launch the Python Flask application and Nginx to act as a front end reverse proxy.

* `nginx` is the folder used for mounting individual API config file of each API service and some static content, like `favicon.ico`. This folder is mounted to the `hubmap-auth` container using docker volumes.

* `sample-api` is an example API service builds its own docker image and runs its own container. In this example, the API service is created with Pythong Flask and serviced by uWSGI. But this image doesn't contain Nginx server. We only use `sample-api.conf` and ask the Nginx from `hubmap-auth` to proxy the API requests. That's why we also put the configuration file in the `nginx/conf.d-dev` and `nginx/conf.d-prod` folder for development and production purposes and it will be mounted to the `hubmap-auth` container when it's spun up.

The `log` under each project is another volume mount, this allows us to access the log files generated from the running contianers on the host for easy debugging and monitoring.

## Overview of tools

- [Docker Engine](https://docs.docker.com/install/)
- [Docker Compose](https://docs.docker.com/compose/install/)

Note: Docker Compose requires Docker to be installed and running first.

## Workflow of setting up multiple HuBMAP docker compose projects

Note: Don't confuse with the term of `service` and `container` when we talk about Docker Compose. A service only runs one image, but it codifies the way that image runs&mdash;what ports it should use, how many replicas of the container should run so the service has the capacity it needs, and so on. That's why in `docker-compose.yml` we see `services` defined.

With a micro-services architecture design, we probably want to share a single database container across two or more applications, so that they can access the same data. Docker and Docker Compose make this possible through the use of Docker networks, allowing containers from different compose projects to be attached to the same network.

### Step 1: get the source code of each project

Currently, you can deploy the following projects with the `gateway`. Git clone the source code of each project and put them under the same parent directory.

- [UUID API](https://github.com/hubmapconsortium/uuid-api) (the `mysql-docker-zhou` branch)
- [Entity API](https://github.com/hubmapconsortium/entity-api) (the `neo4j-docker-zhou` branch)
- [Ingest API](https://github.com/hubmapconsortium/ingest-ui) (the `ingest-api-docker-zhou` branch)

### Step 2: add configuration files for each project

Follow the instructions of each project to setup the configuration. All the projects should share the same Globus APP client ID and secret.

For the `gateway` project, there's an example configuration file **app.cfg.example** which is located at `hubmap-auth/src/instance`. Copy this file and rename it to **app.cfg** with the appropriate information. The configuration is similar for all the API services mentioned above.


Note: MySQL is defiend in the `docker-compose.yml` of the `uuid-api` project and the MySQL root password as well as user information are defiend in the compose yaml file as well. The Neo4j service gets defined in the `entity-api` project and you'll need to set the password for the native `neo4j` user in the `app.cfg` file, which is explained in the `entity-api` project.

### Step 3: build docker images and spin up the containers

In the `gateway` project:

````
sudo chmod +x hubmap-docker.sh
sudo ./hubmap-docker.sh dev
````

The build process will take some time before we have all the running services. 

For production deployment, simply change to:

````
sudo ./hubmap-docker.sh prod
````

The production changes include:

* Removing any volume bindings for application code, so that code stays inside the container and can’t be changed from outside
* Binding to different ports on the host
* Run an `init` inside each container that forwards signals and reaps processes.
* Specifying a restart policy like `restart: always` to avoid downtime