# HuBMAP Gateway With Multi-Container Stack

The HuBMAP Web Gateway serves as an authentication and authorization gateway for the HuBMAP API services. All API requests will be proxied to this gateway service for authentication and authorization against Globus Auth before reaching to the API endpoints. As a result of this design, the API services no longer need to handle the authentication and authorization.

## Development and deployment environments

We have the following 4 development and deployment environments:

* localhost - all the services will be deployed with docker containers including sample Neo4j and sample MySQL are running on the same localhost listing on different ports, without globus data
* dev - all services except ingest-api will be running on AWS EC2 with SSL certificates, Neo4j and MySQL are dev versions on AWS, and ingest-api(and another nginx) will be running on PSC with domain and globus data
* test - similar to dev but for production-like settings with Neo4j and MySQL test versions of database
* prod - similar to test but for production settings with production versions of Neo4j and MySQL

## Project structure

````
gateway
├── api_endpoints.dev.json
├── api_endpoints.localhost.json
├── api_endpoints.prod.json
├── api_endpoints.test.json
├── docker-compose.yml
├── docker-compose.dev.yml
├── docker-compose.localhost.yml
├── docker-compose.prod.yml
├── docker-compose.test.yml
├── hubmap-auth
│   ├── Dockerfile
│   ├── log
│   ├── src
│   └── start.sh
└── nginx
    ├── conf.d-dev
    ├── conf.d-localhost
    ├── conf.d-prod
    ├── conf.d-test
    └── html
````

* `api_endpoints.*.json` are lookup files of all the API endpoints for different environments (localhost, dev, test, and prod). Public endpoints don't need authentication, but private endpoints will require the globus `auth_token` in the custom `MAuthorization` HTTP header. 

* `docker-compose.yml` defines all the services and container details, as well as mounted volumes and ports mapping. `docker-compose.dev.yml` should be used for localhost development along with the base `docker-compose.yml`. `docker-compose.test.yml` and `docker-compose.prod.yml` should be used for testing and production respectively  along with the base `docker-compose.yml`.

* `hubmap-auth` is the actual HuBMAP Web Gateway authentication and authorization service that verifies all the API requests. It basically sets up the uWSGI application server to launch the Python Flask application and Nginx to act as a front end reverse proxy.

* `nginx` is the folder used for mounting individual API config file of each API service and some static content, like `favicon.ico`. This folder is mounted to the `hubmap-auth` container using docker volumes.

The `log` under `hubmap-auth` is another volume mount, this allows us to access the log files generated from the running contianer on the host for easy debugging and monitoring.

## Overview of tools

- [Docker Engine](https://docs.docker.com/install/)
- [Docker Compose](https://docs.docker.com/compose/install/)

Note: Docker Compose requires Docker to be installed and running first.

## Workflow of setting up multiple HuBMAP docker compose projects

With a micro-services architecture design, we probably want to share a single database container across two or more applications, so that they can access the same data. Docker and Docker Compose make this possible through the use of Docker networks, allowing containers from different compose projects to be attached to the same network.

**Note: the following steps only describe the workflow of setting up multiple HuBMAP docker compose projects on local development environment on the same host machine.**

### Step 1: get the source code of each project

Currently, you can deploy the following projects with the `gateway`. Git clone the source code of each project and put them under the same parent directory.

- [UUID API](https://github.com/hubmapconsortium/uuid-api)
- [Entity API](https://github.com/hubmapconsortium/entity-api)
- [Search API](https://github.com/hubmapconsortium/search-api)
- [Ingest API and UI](https://github.com/hubmapconsortium/ingest-ui)
- [Ingest Pipeline](https://github.com/hubmapconsortium/ingest-pipeline) (used for localhost build)

### Step 2: add configuration files for each project

Follow the instructions of each project to setup the configuration. All the projects should share the same Globus APP client ID and secret.

For the `gateway` project, there's an example configuration file **app.cfg.example** which is located at `hubmap-auth/src/instance`. Copy this file and rename it to **app.cfg** with the appropriate information. The configuration is similar for all the API services mentioned above.


Note: MySQL is defiend in the `docker-compose.yml` of the `uuid-api` project and the MySQL root password as well as user information are defiend in the compose yaml file as well. The Neo4j service gets defined in the `entity-api` project and you'll need to set the password for the native `neo4j` user in the `app.cfg` file, which is explained in the `entity-api` project.

### Step 3: build docker images and spin up the containers

In the `gateway` project, first make sure the `hubmap-docker.sh` script is executable, 

````
chmod +x hubmap-docker.sh
````

The usage of this script:

````
./hubmap-docker.sh [localhost|dev|test|prod] [build|start|stop|check|config] [-vh][--no-cache]
````

The `hubmap-docker.sh` basically takes two arguments: deployment environment (localhost|dev|test|prod) and the option (build|start|stop|check|config). In addition, you can also use `-v` to see the verbose output and `-h` for the usage help tip. The `--no-cache` is used with `build` to avoid the docker cache when creating images.

Before we go ahead to start building the docker images, we can do a check to see if all the required configuration files are in place:

````
./hubmap-docker.sh localhost check
````

We can also validate and view the details of corresponding compose files:

````
./hubmap-docker.sh localhost config
````

Building the docker images and starting/stopping the contianers require to use docker daemon, you'll probably need to use `sudo` in the following steps. 

To build all the docker images:

````
sudo ./hubmap-docker.sh localhost build --no-cache
````

The build process will take some time before we have all the docker images created. And the optional `--no-cache` option is to ensure not to use the cache when building the images.

After that, we can start all the services:

````
sudo ./hubmap-docker.sh localhost start
````

This command starts up all the containers and runs the processes inside each container (except the `hubmap-neo4j`, `hubmap-mysql`, `hubmap-elasticsearch`, `hubmap-kibana`, and `ingest-pipeline`) with the user `hubmap` who has the same UID and GID based on the user on the host.

And to stop the services:

````
sudo ./hubmap-docker.sh localhost stop
````

## Testing and Production deployment

For development environment, all the docker images are built on the same host machine and all the containers are running on the same host machine as well. It also comes with a sample Neo4j container and a MySQL database for a full-stack services. However, for testing and production deployment, the `ingest-api` will be running on a separate machine (due to dataset mount) and the Neo4j and MySQL are also running remotely. Additional changes include:

* Removing any volume bindings for application code, so that code stays inside the container and can't be changed from outside
* Binding to different ports on the host
* Run an `init` inside each container that forwards signals and reaps processes.
* Specifying a restart policy like `restart: always` to avoid downtime

Take testing environment for example, when we build the docker images:

````
sudo ./hubmap-docker.sh test build
````

This won't build the images of Neo4j, MySQL (pointing to remote instances via configuration), ingest-api and ingest-ui (deployed on a separate host machine).

The main differences between testing and production are:

* different remote Neo4j and MySQL databases
* different Nginx configurations for API services and UI portals (different subdomains and SSL settings)

## Reload Gateway Nginx for configuration changes

To reload nginx(running on the `hubmap-auth` container) configuration changes, first shell into the `hubmap-auth` container:

````
sudo docker exec -it <hubmap-auth-container-id> bash
````

Then send a reload signal to the master process inside that container:

````
nginx -s reload
````

* Reloading keeps the server running while re-reading any configuration file updates.
* Reloading is safer than restarting because if a syntax error is noticed in a config file, it will not proceed with the reload and your server remains running.
* If there is a syntax error in a config file and you restart, it's possible the server will not restart correctly.


## Update base image

The `entity-api`, `uuid-api`, `ingest-api`, and `hubmap-auth` docker images are based on the `hubmap/api-base-image:latest` image. If you need to update the base image, go to the `api-base-image` directory and recrerate it with:

````
sudo docker build -t hubmap/api-base-image:latest
````

Then publish it to the DockerHub:

````
sudo docker login
sudo docker push hubmap/api-base-image:latest
````
