# HuBMAP Web Gateway With Multi-Container Stack

The HuBMAP Web Gateway serves as an authentication gateway for the HuBMAP API services. All API requests will be passed to this gateway service for authentication and authorization before reaching to the API endpoints. 

## Overview of tools and workflow

- Docker v19.03.2: https://docs.docker.com/install/
- Docker Compose v3.7: https://docs.docker.com/compose/install/

We first use `Dockerfile` to define the image for each service componment. With Docker Compose, we define the services and their relation to each other in the `docker-compose.yml` file. Then spin this multi-container application stack up in a single command which does everything that needs to be done to get it running. 


## Build stack images with Docker Compose

````
docker-compose build --no-cache
````

The build subcommand will build all the images that are specified in the Compose file. The command will go through all services in the `docker-compose.yml` file and build the ones that have a build section defined. In our case, it will build two new images for `viz` and `nlp`.


## Start up the stack

````
docker-compose up
````

This command spins up all the containers defiened in the `docker-compose.yml` and you will see the logs of the containers in stdout.

Once the stack is up running, you'll be able to access the Sample API service at `http://localhost:8181/`. The Gateway is running at `http://localhost:8080` for API authentication and authorization purposes. 

If you want to run the containers in detached mode:

````
docker-compose up -d
````

The `-d` option made the `docker-compose` command return.

## Stop or remove the containers

To safely stop all the active services in the stack:

````
docker-compose stop
````
The above command will preserve containers, volumes, and networks, along with every modification made to them.

Instead of stopping all the containers, you can also specifically stop a particular service:

````
docker-compose stop <container-name>
````

To reset the status of our project:

````
docker-compose down
````

The above command will stop your containers, and it also removes the stopped containers as well as any networks that were created.

You can take `down` 1 step further and add the `-v` flag to remove all volumes too. This is great for doing a full blown reset on your environment by running:

````
docker-compose down -v
````

## Restart containers

````
docker-compose restart
````

This command restarts all stopped and running services. To just restart a particular container but not other containers:

````
docker-compose restart <container-name>
````

## Debugging

We can list all running containers:

````
docker container ls
````

Then we can get into a container;s shell by running:

````
docker exec -it <mycontainer> bash
````

From inside the container, we can check the log file, etc...
