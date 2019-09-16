# HuBMAP Web Gateway With Multi-Container Stack

The HuBMAP Web Gateway serves as an authentication and authorization gateway for the HuBMAP API services. All API requests will be proxied to this gateway service for authentication and authorization before reaching to the API endpoints. As a result of this design, the API services no longer need to handle the authentication and authorization.

## Overview of tools

- [Docker v19.03.2](https://docs.docker.com/install/)
- [Docker Compose v3.7](https://docs.docker.com/compose/install/)

Note: Docker Compose requires Docker to be installed and running first.

## Workflow

We first use individual `Dockerfile` to define the image for each service componment. Then with Docker Compose, we define all the services and their relation to each other in the `docker-compose.yml` file. This allows us to spin this multi-container application stack up in a single command which does everything that needs to be done to get it running. 


### Build images

````
docker-compose build --no-cache
````

The command will go through all services in the `docker-compose.yml` file and build the ones that have a build section defined. 


## Start up services

````
docker-compose up
````

This command spins up all the containers defiened in the `docker-compose.yml` and aggregates the output of each container. When the command exits, all containers are stopped. Running `docker-compose up -d` starts the containers in the background and leaves them running.

Once the stack is up running, you'll be able to access the Sample API service at `http://localhost:8181/`. The Gateway is running at `http://localhost:8080` for API authentication and authorization purposes. 


### Stop the running containers

````
docker-compose stop
````
The above command stops all the running containers without removing them. It preserves containers, volumes, and networks, along with every modification made to them. The stopped containers can be started again with `docker-compose start`. 

Instead of stopping all the containers, you can also specifically stop a particular service:

````
docker-compose stop <service-name>
````

## Restart

````
docker-compose restart
````

This restarts all stopped and running services. If you make changes to your `docker-compose.yml` configuration or the individual `Dockerfile` these changes are not reflected after running this restart command. You'll need to rebuild all the images.

To just restart a particular service but not other services:

````
docker-compose restart <service-name>
````

### Reset the status of our project

````
docker-compose down
````

This command stops containers and removes containers, networks, volumes, and images created by `docker-compose up`.

You can take `down` 1 step further and add the `-v` flag to remove all volumes too. This is great for doing a full blown reset on your environment by running:

````
docker-compose down -v
````

## Debugging

We can list all running containers:

````
docker container ls
````

Then we can get into a container's shell by running:

````
docker exec -it <mycontainer> bash
````

